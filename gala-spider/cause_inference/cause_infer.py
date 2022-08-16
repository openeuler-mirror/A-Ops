import random
from typing import List

import networkx as nx
from scipy.stats import pearsonr
from scipy.special import expit

from spider.util import logger
from spider.conf.observe_meta import RelationType
from spider.conf.observe_meta import ObserveMetaMgt
from spider.collector.data_collector import DataCollector
from spider.collector.prometheus_collector import PrometheusCollector
from cause_inference.exceptions import InferenceException
from cause_inference.exceptions import DBException
from cause_inference.exceptions import MetadataException
from cause_inference.exceptions import DataParseException
from cause_inference.config import infer_config
from cause_inference.rule_parser import rule_engine
from cause_inference.arangodb import connect_to_arangodb
from cause_inference.arangodb import query_recent_topo_ts
from cause_inference.arangodb import query_topo_entities
from cause_inference.arangodb import query_subgraph


def _get_metric_obj_type(metric_id: str):
    if not metric_id.startswith(infer_config.data_agent + "_"):
        raise MetadataException('Data source of the metric {} can not be identified.'.format(metric_id))

    left = metric_id[len(infer_config.data_agent) + 1:]
    obsv_types = ObserveMetaMgt().get_observe_types()
    for obj_type in obsv_types:
        if left.startswith(obj_type.value + "_"):
            return obj_type.value

    raise MetadataException('Entity type of the metric {} can not be supported.'.format(metric_id))


def normalize_abn_score(score):
    return expit(score)


class AbnormalEvent:
    def __init__(self, timestamp, abnormal_metric_id, abnormal_score, metric_labels):
        self.timestamp = timestamp
        self.abnormal_metric_id = abnormal_metric_id
        self.abnormal_score = abnormal_score
        self.metric_labels = metric_labels
        self.hist_data = []

    def __repr__(self):
        return 'AbnormalEvent(timestamp={}, abnormal_metric_id="{}", abnormal_score={}, metric_labels={})'.format(
            self.timestamp,
            self.abnormal_metric_id,
            self.abnormal_score,
            self.metric_labels,
        )

    def set_hist_data(self, hist_data):
        self.hist_data = hist_data[:]

    def to_dict(self):
        res = {
            'metric_id': self.abnormal_metric_id,
            'timestamp': self.timestamp,
            'abnormal_score': self.abnormal_score,
            'metric_labels': self.metric_labels,
        }
        return res


class CausalGraph:
    def __init__(self, raw_topo_graph, abnormal_kpi: AbnormalEvent, abnormal_metrics: List[AbnormalEvent],
                 orig_abn_kpi: AbnormalEvent = None):
        self.topo_nodes = raw_topo_graph.get('vertices', {})
        self.topo_edges = raw_topo_graph.get('edges', {})
        self.abnormal_kpi: AbnormalEvent = abnormal_kpi
        self.abnormal_metrics: List[AbnormalEvent] = abnormal_metrics
        self.orig_abn_kpi: AbnormalEvent = orig_abn_kpi

        self.node_id_of_abn_kpi = None
        self.causal_graph = nx.DiGraph()
        self.init_casual_graph()

    def init_casual_graph(self):
        for node_id, node_attrs in self.topo_nodes.items():
            self.causal_graph.add_node(node_id, **node_attrs)
            self.set_abnormal_status_of_node(node_id, False)

        # 标记有异常指标的节点
        abnormal_metrics = [self.abnormal_kpi]
        abnormal_metrics.extend(self.abnormal_metrics)
        for abn_metric in abnormal_metrics:
            try:
                entity_keys_of_metric = get_entity_keys_of_metric(abn_metric.abnormal_metric_id,
                                                                  abn_metric.metric_labels)
            except MetadataException as ex:
                logger.logger.error(ex)
                continue
            for node_id in self.causal_graph.nodes:
                if not self.is_metric_matched_to_node(node_id, entity_keys_of_metric):
                    continue

                if abn_metric.abnormal_metric_id == self.abnormal_kpi.abnormal_metric_id:
                    self.node_id_of_abn_kpi = node_id

                self.set_abnormal_status_of_node(node_id, True)
                self.append_abnormal_metric_to_node(node_id, abn_metric)
                break

    def is_metric_matched_to_node(self, node_id, entity_keys_of_metric):
        matched = True
        node_attrs = self.causal_graph.nodes[node_id]
        for key in entity_keys_of_metric:
            if node_attrs.get(key) != entity_keys_of_metric[key]:
                matched = False
                break
        return matched

    def prune_by_abnormal_node(self):
        node_ids = list(self.causal_graph.nodes)
        for node_id in node_ids:
            if not self.is_abnormal_of_node(node_id):
                self.causal_graph.remove_node(node_id)

    def set_abnormal_status_of_node(self, node_id, abnormal_status):
        self.causal_graph.nodes[node_id]['is_abnormal'] = abnormal_status

    def is_abnormal_of_node(self, node_id):
        if 'is_abnormal' not in self.causal_graph.nodes[node_id]:
            return False
        return self.causal_graph.nodes[node_id]['is_abnormal']

    def append_abnormal_metric_to_node(self, node_id, abn_metric):
        node_attrs = self.causal_graph.nodes[node_id]
        abn_metrics = node_attrs.setdefault('abnormal_metrics', [])
        exist = False
        # 去除（在不同时间点上）重复的异常metric
        for i, metric in enumerate(abn_metrics):
            if metric.abnormal_metric_id == abn_metric.abnormal_metric_id:
                if abn_metric.timestamp > metric.timestamp:
                    abn_metrics[i] = abn_metric
                exist = True
        if not exist:
            abn_metrics.append(abn_metric)

    def get_abnormal_metrics_of_node(self, node_id):
        return self.causal_graph.nodes[node_id].get('abnormal_metrics', [])

    def get_abnormal_metric_of_node(self, node_id, idx):
        return self.causal_graph.nodes[node_id].get('abnormal_metrics')[idx]


class Cause:
    def __init__(self, cause_node: dict, cause_metric: AbnormalEvent, cause_score):
        self.cause_node = cause_node
        self.cause_metric = cause_metric
        self.cause_score = cause_score

    def to_dict(self):
        res = {
            'cause_metric': self.cause_metric.to_dict(),
            'cause_score': self.cause_score,
            'cause_entity_id': self.cause_node.get('_id'),
        }
        return res


# 因果推理
class CauseInferring:
    def __init__(self, rou=0.05, random_walk_round=10000, default_window_size=1000):
        self.rou = rou
        self.random_walk_round = random_walk_round
        if self.random_walk_round <= 0:
            raise InferenceException('Random walk round of cause inferring algorithm can not be less than zero')
        self.default_window_size = default_window_size
        self.abn_kpi_idx = None
        self.transfer_matrix = {}

    @staticmethod
    def calc_corr(data1, data2):
        valid_len = min(len(data1), len(data2))
        corr = pearsonr(data1[len(data1)-valid_len:], data2[len(data2)-valid_len:])
        if str(corr[0]) == 'nan':
            return 0.0001
        return corr[0]

    def inferring(self, causal_graph: CausalGraph, top_k=3) -> List[Cause]:
        res = []

        abn_kpi = causal_graph.abnormal_kpi
        node_id_of_abn_kpi = causal_graph.node_id_of_abn_kpi
        if not node_id_of_abn_kpi:
            logger.logger.error('Can not find observe node of the abnormal kpi.')
            return []
        for i, abn_metric in enumerate(causal_graph.get_abnormal_metrics_of_node(node_id_of_abn_kpi)):
            if abn_metric.abnormal_metric_id == abn_kpi.abnormal_metric_id:
                self.abn_kpi_idx = (node_id_of_abn_kpi, i)
                break
        if self.abn_kpi_idx is None:
            logger.logger.error('Abnormal kpi is None.')
            return res

        # 计算转移概率矩阵
        self.transfer_matrix.clear()
        for node_id in causal_graph.causal_graph.nodes:
            for i, _ in enumerate(causal_graph.get_abnormal_metrics_of_node(node_id)):
                metric_idx = (node_id, i)
                self.transfer_matrix.setdefault(metric_idx, {})
                self.calc_transfer_probs(metric_idx, causal_graph)

        walk_nums = self.one_order_random_walk()
        cause_res = list(walk_nums.items())
        cause_res = sorted(cause_res, key=lambda k: k[1], reverse=True)
        cause_res = cause_res[:top_k]

        for item in cause_res:
            metric_idx = item[0]
            score = item[1]
            cause_node_attrs = causal_graph.causal_graph.nodes[metric_idx[0]]
            cause_metric = causal_graph.get_abnormal_metric_of_node(metric_idx[0], metric_idx[1])
            try:
                uni_score = score / self.random_walk_round
            except ZeroDivisionError as ex:
                raise InferenceException(ex) from ex
            cause = Cause(cause_node_attrs, cause_metric, uni_score)
            res.append(cause)

        return res

    def calc_transfer_probs(self, src_metric_idx, causal_graph: CausalGraph):
        probs = self.transfer_matrix.get(src_metric_idx)
        src_abn_metric = causal_graph.get_abnormal_metric_of_node(src_metric_idx[0], src_metric_idx[1])

        # 计算前向转移概率
        max_corr = 0
        for node_id in causal_graph.causal_graph.pred.get(src_metric_idx[0]):
            for i, tgt_abn_metric in enumerate(causal_graph.get_abnormal_metrics_of_node(node_id)):
                tgt_metric_idx = (node_id, i)
                corr = abs(tgt_abn_metric.abnormal_score)
                max_corr = max(max_corr, corr)
                probs.setdefault(tgt_metric_idx, corr)

        # 计算后向转移概率
        for node_id in causal_graph.causal_graph.succ.get(src_metric_idx[0]):
            for i, tgt_abn_metric in enumerate(causal_graph.get_abnormal_metrics_of_node(node_id)):
                tgt_metric_idx = (node_id, i)
                corr = abs(tgt_abn_metric.abnormal_score)
                probs.setdefault(tgt_metric_idx, corr * self.rou)

        # 计算自向转移概率
        corr = max(0, abs(src_abn_metric.abnormal_score) - max_corr)
        probs.setdefault(src_metric_idx, corr)

        # 正则化
        total = sum(probs.values())
        for tgt_metric_idx, corr in probs.items():
            try:
                probs[tgt_metric_idx] = corr / total
            except ZeroDivisionError as ex:
                raise InferenceException('Sum of transition probability can not be zero') from ex

    def one_order_random_walk(self):
        walk_nums = {}
        curr_node_idx = self.abn_kpi_idx
        rwr = self.random_walk_round
        round_ = 0
        while round_ < rwr:
            next_node_idx = self.get_next_walk_node(curr_node_idx)
            num = walk_nums.setdefault(next_node_idx, 0)
            walk_nums.update({next_node_idx: num + 1})
            round_ += 1

        return walk_nums

    def get_next_walk_node(self, curr_metric_idx):
        # 随机选择
        probs = self.transfer_matrix.get(curr_metric_idx)
        prob = random.random()
        next_node_idx = curr_metric_idx
        for node_idx, node_prob in probs.items():
            if prob < node_prob:
                next_node_idx = node_idx
                break
            else:
                prob -= node_prob

        return next_node_idx


def get_entity_keys_of_metric(metric_id, metric_labels):
    metric_entity_type = _get_metric_obj_type(metric_id)
    observe_meta = ObserveMetaMgt().get_observe_meta(metric_entity_type)
    if observe_meta is None:
        raise MetadataException('Can not find observe meta info, observe type={}'.format(metric_entity_type))

    key_labels = {}
    for entity_key in observe_meta.keys:
        if entity_key not in metric_labels:
            raise MetadataException('Observe entity key[{}] miss of metric[{}].'.format(entity_key, metric_id))
        key_labels[entity_key] = metric_labels[entity_key]

    return key_labels


def get_entity_labels_of_metric(metric_id, metric_labels):
    metric_entity_type = _get_metric_obj_type(metric_id)
    observe_meta = ObserveMetaMgt().get_observe_meta(metric_entity_type)
    if observe_meta is None:
        raise MetadataException('Can not find observe meta info, observe type={}'.format(metric_entity_type))

    labels = {'type': metric_entity_type}
    for entity_key in observe_meta.keys:
        if entity_key in metric_labels:
            labels[entity_key] = metric_labels[entity_key]
    for entity_label in observe_meta.labels:
        if entity_label in metric_labels:
            labels[entity_label] = metric_labels[entity_label]

    return labels


def complete_key_info_of_metric(metric_labels, observe_entity):
    observe_meta = ObserveMetaMgt().get_observe_meta(observe_entity.get('type'))
    if not observe_meta:
        raise MetadataException('Can not find observe meta info, observe type={}'.format(observe_entity.get('type')))
    for entity_key in observe_meta.keys:
        metric_labels[entity_key] = observe_entity.get(entity_key)


def query_abnormal_topo_subgraph(abnormal_event: AbnormalEvent):
    abn_ts = int(float(abnormal_event.timestamp))
    abn_metric_id = abnormal_event.abnormal_metric_id
    abn_metric_labels = abnormal_event.metric_labels

    # 1. 连接 arangodb 图数据库
    db = connect_to_arangodb(infer_config.arango_conf.get('url'), infer_config.arango_conf.get('db_name'))

    # 2. 查询异常事件时间戳附近已保存拓扑关系图的时间戳
    recent_ts = query_recent_topo_ts(db, abn_ts)
    if abn_ts - recent_ts > infer_config.infer_conf.get('tolerated_bias'):
        raise DBException('The queried topological graph is too old.')

    # 3. 获取异常KPI对应的观测对象实例
    labels = get_entity_labels_of_metric(abn_metric_id, abn_metric_labels)
    abn_entities = query_topo_entities(db, recent_ts, query_options=labels)
    if len(abn_entities) > 1:
        raise InferenceException('Multiple observe entities of abnormal metric found, please check.')
    abn_entity = abn_entities[0]
    complete_key_info_of_metric(abn_metric_labels, abn_entity)

    # 4. 获取拓扑子图
    edge_collection = [
        RelationType.BELONGS_TO.value,
        RelationType.RUNS_ON.value,
    ]
    subgraph = query_subgraph(db, recent_ts, abn_entity.get('_id'), edge_collection,
                              depth=infer_config.infer_conf.get('topo_depth'))
    vertices = subgraph.get('vertices')
    vertices.setdefault(abn_entity.get('_id'), abn_entity)
    return subgraph


def clear_aging_evts(all_metric_evts: List[AbnormalEvent], latest_ts) -> List[AbnormalEvent]:
    res = []
    for metric_evt in all_metric_evts:
        if metric_evt.timestamp + infer_config.infer_conf.get('evt_aging_duration') < latest_ts:
            continue
        res.append(metric_evt)
    return res


def filter_valid_evts(all_metric_evts: List[AbnormalEvent], latest_ts) -> List[AbnormalEvent]:
    res = []
    for metric_evt in all_metric_evts:
        if metric_evt.timestamp + infer_config.infer_conf.get('evt_valid_duration') < latest_ts:
            continue
        if metric_evt.timestamp > latest_ts:
            continue
        res.append(metric_evt)
    return res


def parse_abn_evt(data) -> AbnormalEvent:
    resource = data.get('Resource')
    if not resource:
        raise DataParseException('Atribute "Resource" required in abnormal event')
    abn_evt = AbnormalEvent(
        data.get('Timestamp'),
        resource.get('metric_id'),
        1.0,
        resource.get('metric_label')
    )
    return abn_evt


def query_hist_data_of_abn_metric(causal_graph):
    collector: DataCollector = PrometheusCollector(base_url=infer_config.prometheus_conf.get('base_url'),
                                                   range_api=infer_config.prometheus_conf.get('range_api'),
                                                   step=infer_config.prometheus_conf.get('step'))
    abn_ts = causal_graph.abnormal_kpi.timestamp
    for node_id in causal_graph.causal_graph.nodes:
        for abn_metric in causal_graph.get_abnormal_metrics_of_node(node_id):
            orig_abn_metric = abn_metric
            if (abn_metric.abnormal_metric_id == causal_graph.abnormal_kpi.abnormal_metric_id and
                    causal_graph.orig_abn_kpi is not None):
                orig_abn_metric = causal_graph.orig_abn_kpi
            end_ts = abn_ts
            start_ts = end_ts - infer_config.infer_conf.get('sample_duration')
            query_options = get_entity_keys_of_metric(orig_abn_metric.abnormal_metric_id, orig_abn_metric.metric_labels)
            data_records = collector.get_range_data(orig_abn_metric.abnormal_metric_id, start_ts, end_ts,
                                                    query_options=query_options)
            if len(data_records) == 0:
                raise InferenceException(
                    'No history data of the abnormal metric {}'.format(orig_abn_metric.abnormal_metric_id)
                )
            hist_data = [float(record.metric_value) for record in data_records]
            abn_metric.set_hist_data(hist_data)


def cause_locating(abnormal_kpi: AbnormalEvent, abnormal_metrics: List[AbnormalEvent],
                   orig_abn_kpi: AbnormalEvent = None) -> List[Cause]:
    # 1. 根据异常事件获取异常KPI对应的观测对象
    # 2. 以异常观测对象为中心，查询图数据库，获取拓扑子图
    abn_subgraph = query_abnormal_topo_subgraph(abnormal_kpi)

    # 3. 基于专家规则，补全拓扑子图的隐式因果关系
    causal_graph = CausalGraph(abn_subgraph, abnormal_kpi, abnormal_metrics, orig_abn_kpi)
    rule_engine.rule_parsing(causal_graph)
    # 4. 根据异常观测对象（存在异常指标的观测对象）对拓扑子图进行剪枝，构建故障传播图
    causal_graph.prune_by_abnormal_node()

    logger.logger.debug("Causal graph nodes are: {}".format(causal_graph.causal_graph.nodes))
    logger.logger.debug("Causal graph predecessors: {}".format(causal_graph.causal_graph.pred))
    logger.logger.debug("Causal graph successors: {}".format(causal_graph.causal_graph.succ))

    # 5. 以故障传播图 + 异常KPI为输入，执行根因推导算法，输出 top3 根因指标
    infer_engine = CauseInferring()
    causes = infer_engine.inferring(causal_graph, top_k=infer_config.infer_conf.get('root_topk'))
    logger.logger.debug('=========inferring result: =============')
    for i, cause in enumerate(causes):
        logger.logger.debug('The top {} root metric output:'.format(i+1))
        logger.logger.debug('abnormal timestamp is: {}, abnormal metric is: {}, abnormal observe entity is: {}'.format(
            cause.cause_metric.timestamp,
            cause.cause_metric.abnormal_metric_id,
            cause.cause_node.get('_id'),
        ))
        logger.logger.debug('abnormal score is: {}'.format(cause.cause_score))

    return causes
