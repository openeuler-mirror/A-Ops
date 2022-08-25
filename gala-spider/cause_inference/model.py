from typing import List

import networkx as nx

from cause_inference.config import infer_config
from cause_inference.exceptions import MetadataException
from spider.conf.observe_meta import ObserveMetaMgt
from spider.util import logger


def get_metric_obj_type(metric_id: str):
    if not metric_id.startswith(infer_config.data_agent + "_"):
        raise MetadataException('Data source of the metric {} can not be identified.'.format(metric_id))

    left = metric_id[len(infer_config.data_agent) + 1:]
    obsv_types = ObserveMetaMgt().get_observe_types()
    for obj_type in obsv_types:
        if left.startswith(obj_type + "_"):
            return obj_type

    raise MetadataException('Entity type of the metric {} can not be supported.'.format(metric_id))


def get_entity_keys_of_metric(metric_id, metric_labels):
    metric_entity_type = get_metric_obj_type(metric_id)
    observe_meta = ObserveMetaMgt().get_observe_meta(metric_entity_type)
    if observe_meta is None:
        raise MetadataException('Can not find observe meta info, observe type={}'.format(metric_entity_type))

    key_labels = {}
    for entity_key in observe_meta.keys:
        if entity_key not in metric_labels:
            raise MetadataException('Observe entity key[{}] miss of metric[{}].'.format(entity_key, metric_id))
        key_labels[entity_key] = metric_labels[entity_key]

    return key_labels


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

        self.entity_id_of_abn_kpi = None
        self.entity_cause_graph = nx.DiGraph()
        self.metric_cause_graph = nx.DiGraph()
        self.init_casual_graph()

    def init_casual_graph(self):
        for node_id, node_attrs in self.topo_nodes.items():
            self.entity_cause_graph.add_node(node_id, **node_attrs)
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
            for node_id in self.entity_cause_graph.nodes:
                if not self.is_metric_matched_to_node(node_id, entity_keys_of_metric):
                    continue
                if abn_metric.abnormal_metric_id == self.abnormal_kpi.abnormal_metric_id:
                    self.entity_id_of_abn_kpi = node_id
                self.set_abnormal_status_of_node(node_id, True)
                self.append_abnormal_metric_to_node(node_id, abn_metric)
                break

    def is_metric_matched_to_node(self, node_id, entity_keys_of_metric):
        node_attrs = self.entity_cause_graph.nodes[node_id]
        for key in entity_keys_of_metric:
            if node_attrs.get(key) != entity_keys_of_metric[key]:
                return False
        return True

    def prune_by_abnormal_node(self):
        node_ids = list(self.entity_cause_graph.nodes)
        for node_id in node_ids:
            if not self.is_abnormal_of_node(node_id):
                self.entity_cause_graph.remove_node(node_id)

    def set_abnormal_status_of_node(self, node_id, abnormal_status):
        self.entity_cause_graph.nodes[node_id]['is_abnormal'] = abnormal_status

    def is_abnormal_of_node(self, node_id):
        if 'is_abnormal' not in self.entity_cause_graph.nodes[node_id]:
            return False
        return self.entity_cause_graph.nodes[node_id]['is_abnormal']

    def append_abnormal_metric_to_node(self, node_id, abn_metric):
        node_attrs = self.entity_cause_graph.nodes[node_id]
        abn_metrics = node_attrs.setdefault('abnormal_metrics', [])
        # 去除（在不同时间点上）重复的异常metric
        for i, metric in enumerate(abn_metrics):
            if metric.abnormal_metric_id == abn_metric.abnormal_metric_id:
                if abn_metric.timestamp > metric.timestamp:
                    abn_metrics[i] = abn_metric
                return
        abn_metrics.append(abn_metric)

    def get_abnormal_metrics_of_node(self, node_id):
        return self.entity_cause_graph.nodes[node_id].get('abnormal_metrics', [])

    def get_abnormal_metric_of_node(self, node_id, idx):
        return self.entity_cause_graph.nodes[node_id].get('abnormal_metrics')[idx]

    def init_metric_cause_graph(self):
        for entity_id in self.entity_cause_graph.nodes:
            for metric_evt in self.get_abnormal_metrics_of_node(entity_id):
                self.metric_cause_graph.add_node((entity_id, metric_evt.abnormal_metric_id), **metric_evt.to_dict())
        for edge in self.entity_cause_graph.edges:
            from_entity_id = edge[0]
            to_entity_id = edge[1]
            for from_metric_evt in self.get_abnormal_metrics_of_node(from_entity_id):
                for to_metric_evt in self.get_abnormal_metrics_of_node(to_entity_id):
                    self.metric_cause_graph.add_edge(
                        (from_entity_id, from_metric_evt.abnormal_metric_id),
                        (to_entity_id, to_metric_evt.abnormal_metric_id)
                    )


class Cause:
    def __init__(self, metric_id, entity_id, cause_score, path=None):
        self.metric_id = metric_id
        self.entity_id = entity_id
        self.cause_score = cause_score
        self.path = path or []

    def to_dict(self):
        res = {
            'metric_id': self.metric_id,
            'entity_id': self.entity_id,
            'cause_score': self.cause_score
        }
        return res
