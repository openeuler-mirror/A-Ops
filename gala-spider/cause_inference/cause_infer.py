from typing import List

from scipy.special import expit

from cause_inference.model import Cause
from cause_inference.model import CausalGraph
from cause_inference.model import AbnormalEvent
from spider.util import logger
from spider.conf.observe_meta import RelationType
from spider.conf.observe_meta import ObserveMetaMgt
from spider.collector.data_collector import DataCollector
from spider.collector.prometheus_collector import PrometheusCollector
from cause_inference.exceptions import InferenceException
from cause_inference.exceptions import DBException
from cause_inference.exceptions import DataParseException
from cause_inference.config import infer_config
from cause_inference.rule_parser import rule_engine
from cause_inference.arangodb import connect_to_arangodb
from cause_inference.arangodb import query_recent_topo_ts
from cause_inference.arangodb import query_topo_entities
from cause_inference.arangodb import query_subgraph
from cause_inference.infer_policy import InferPolicy
from cause_inference.infer_policy import get_infer_policy


def normalize_abn_score(score):
    return expit(score)


# 因果推理
class CauseInferring:
    def __init__(self, infer_policy: InferPolicy, top_k=1):
        self.infer_policy = infer_policy
        self.top_k = top_k

    def inferring(self, causal_graph: CausalGraph) -> List[Cause]:
        causes = self.infer_policy.infer(causal_graph, self.top_k)
        return causes


def query_abnormal_topo_subgraph(abnormal_event: AbnormalEvent):
    abn_ts = int(float(abnormal_event.timestamp)) // 1000

    # 1. 连接 arangodb 图数据库
    db = connect_to_arangodb(infer_config.arango_conf.get('url'), infer_config.arango_conf.get('db_name'))

    # 2. 查询异常事件时间戳附近已保存拓扑关系图的时间戳
    recent_ts = query_recent_topo_ts(db, abn_ts)
    if abn_ts - recent_ts > infer_config.infer_conf.get('tolerated_bias'):
        raise DBException('The queried topological graph is too old.')

    # 3. 获取异常KPI对应的观测对象实例
    labels = {'_key': abnormal_event.abnormal_entity_id}
    abn_entities = query_topo_entities(db, recent_ts, query_options=labels)
    if len(abn_entities) > 1:
        raise InferenceException('Multiple observe entities of abnormal metric found, please check.')
    abn_entity = abn_entities[0]

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


def parse_abn_evt(data) -> AbnormalEvent:
    resource = data.get('Resource', {})
    attrs = data.get('Attributes', {})
    if not resource.get('metrics'):
        raise DataParseException('Atribute "Resource.metrics" required in abnormal event')
    if not attrs.get('entity_id') and not resource.get('metric_label'):
        raise DataParseException('metric_label or entity_id info need in abnormal event')
    abn_evt = AbnormalEvent(
        timestamp=data.get('Timestamp'),
        abnormal_metric_id=resource.get('metrics'),
        abnormal_score=1.0,
        metric_labels=resource.get('metric_label'),
        abnormal_entity_id=attrs.get('entity_id'),
    )
    return abn_evt


def parse_entity_id(orig_entity_id: str) -> str:
    fs_idx = orig_entity_id.index('/')
    return orig_entity_id[fs_idx+1:]


def query_hist_data_of_abn_metric(causal_graph):
    collector: DataCollector = PrometheusCollector(base_url=infer_config.prometheus_conf.get('base_url'),
                                                   range_api=infer_config.prometheus_conf.get('range_api'),
                                                   step=infer_config.prometheus_conf.get('step'))
    abn_ts = causal_graph.abnormal_kpi.timestamp
    obsv_meta_mgt = ObserveMetaMgt()
    for node_id in causal_graph.causal_graph.nodes:
        for abn_metric in causal_graph.get_abnormal_metrics_of_node(node_id):
            end_ts = abn_ts
            start_ts = end_ts - infer_config.infer_conf.get('sample_duration')
            query_options = obsv_meta_mgt.get_entity_keys_of_metric(abn_metric.abnormal_metric_id,
                                                                    abn_metric.metric_labels)
            data_records = collector.get_range_data(abn_metric.abnormal_metric_id, start_ts, end_ts,
                                                    query_options=query_options)
            if len(data_records) == 0:
                raise InferenceException(
                    'No history data of the abnormal metric {}'.format(abn_metric.abnormal_metric_id)
                )
            hist_data = [float(record.metric_value) for record in data_records]
            abn_metric.set_hist_data(hist_data)


def format_infer_result(causes, causal_graph):
    abnormal_kpi = causal_graph.abnormal_kpi
    abn_kpi = {
        'metric_id': abnormal_kpi.abnormal_metric_id,
        'entity_id': abnormal_kpi.abnormal_entity_id,
        'timestamp': abnormal_kpi.timestamp,
        'metric_labels': abnormal_kpi.metric_labels
    }
    cause_metrics = []
    metric_cause_graph = causal_graph.metric_cause_graph
    for cause in causes:
        node_attrs = metric_cause_graph.nodes[(cause.entity_id, cause.metric_id)]
        cause_metric = {
            'metric_id': cause.metric_id,
            'entity_id': parse_entity_id(cause.entity_id),
            'metric_labels': node_attrs.get('metric_labels', {}),
            'timestamp': node_attrs.get('timestamp'),
        }
        path = []
        for node_id in cause.path:
            attrs = metric_cause_graph.nodes[node_id]
            path.append({
                'metric_id': node_id[1],
                'entity_id': parse_entity_id(node_id[0]),
                'metric_labels': attrs.get('metric_labels', {}),
                'timestamp': attrs.get('timestamp')
            })
        cause_metric['path'] = path
        cause_metrics.append(cause_metric)
    res = {
        'abnormal_kpi': abn_kpi,
        'cause_metrics': cause_metrics
    }
    return res


def cause_locating(abnormal_kpi: AbnormalEvent, abnormal_metrics: List[AbnormalEvent]):
    # 1. 根据异常事件获取异常KPI对应的观测对象
    # 2. 以异常观测对象为中心，查询图数据库，获取拓扑子图
    abn_topo_subgraph = query_abnormal_topo_subgraph(abnormal_kpi)

    # 3. 基于专家规则，补全拓扑子图的隐式因果关系
    causal_graph = CausalGraph(abn_topo_subgraph, abnormal_kpi, abnormal_metrics)
    rule_engine.rule_parsing(causal_graph)
    # 4. 根据异常观测对象（存在异常指标的观测对象）对拓扑子图进行剪枝，构建故障传播图
    causal_graph.prune_by_abnormal_node()
    # 5. 生成异常指标之间的因果图
    causal_graph.init_metric_cause_graph()

    logger.logger.debug("Causal graph nodes are: {}".format(causal_graph.entity_cause_graph.nodes))
    logger.logger.debug("Causal graph predecessors: {}".format(causal_graph.entity_cause_graph.pred))
    logger.logger.debug("Causal graph successors: {}".format(causal_graph.entity_cause_graph.succ))

    # 6. 以故障传播图 + 异常KPI为输入，执行根因推导算法，输出 topK 根因指标
    infer_policy = get_infer_policy(infer_config.infer_conf.get('infer_policy'))
    infer_engine = CauseInferring(infer_policy, top_k=infer_config.infer_conf.get('root_topk'))
    causes = infer_engine.inferring(causal_graph)
    logger.logger.debug('=========inferring result: =============')
    for i, cause in enumerate(causes):
        logger.logger.debug('The top {} root metric output:'.format(i+1))
        logger.logger.debug('cause metric is: {}, cause entity is: {}, cause score is: {}'.format(
            cause.metric_id,
            cause.entity_id,
            cause.cause_score,
        ))

    res = format_infer_result(causes, causal_graph)
    return res
