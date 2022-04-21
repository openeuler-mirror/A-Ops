from typing import List
from typing import Dict
import time

from spider.conf.observe_meta import ObserveMetaMgt
from spider.conf.observe_meta import ObserveMeta
from spider.data_process.processor import DataProcessor
from spider.entity_mgt import ObserveEntity
from spider.entity_mgt import ObserveEntityCreator
from spider.collector.data_collector import DataRecord
from spider.collector.data_collector import Label
from spider.collector.prometheus_collector import PrometheusCollector
from spider.conf import SpiderConfig
from spider.util import logger


def _filter_unique_labels(labels: List[Label], entity_keys: List[str]) -> Dict[str, str]:
    res = {}

    for label in labels:
        if label.name not in entity_keys:
            continue
        res[label.name] = label.value

    return res


def _id_of_keys(keys: Dict[str, str], entity_keys: List[str]) -> (bool, tuple):
    tmp = []
    for key in entity_keys:
        if key not in keys:
            logger.logger.debug("Key {} not exist.".format(key))
            return False, ()
        tmp.append((key, keys.get(key)))
    return True, tuple(tmp)


class PrometheusProcessor(DataProcessor):

    def collect_observe_entity(self, observe_meta: ObserveMeta, timestamp: float = None) -> List[DataRecord]:
        """
        采集某个观测对象的实例数据。
        例：
        输入：observe_meta = ObserveMeta(type="tcp_link", keys=["machine_id"], metrics=["rx_bytes", "tx_bytes"]),
             timestamp = 0
        输出：res = [
                 DataRecord(metric_id="xxx_tcp_link_rx_bytes", timestamp=0, metric_value=1,
                            labels=[Label(name="machine_id", value="machine1")]),
                 DataRecord(metric_id="xxx_tcp_link_rx_bytes", timestamp=0, metric_value=2,
                            labels=[Label(name="machine_id", value="machine2")]),
                 DataRecord(metric_id="xxx_tcp_link_tx_bytes", timestamp=0, metric_value=3,
                            labels=[Label(name="machine_id", value="machine1")]),
                 DataRecord(metric_id="xxx_tcp_link_tx_bytes", timestamp=0, metric_value=4,
                            labels=[Label(name="machine_id", value="machine2")]),
             ]
        @param observe_meta: 某个观测对象的元数据信息
        @param timestamp: 采集的时间戳
        @return: 某个观测对象在给定时间戳的所有实例数据
        """
        res = []
        timestamp = time.time() if timestamp is None else timestamp
        for metric in observe_meta.metrics:
            metric_id = self._get_metric_id(observe_meta.type, metric)
            data = PrometheusCollector(**SpiderConfig().prometheus_conf).get_instant_data(metric_id, timestamp)
            if len(data) > 0:
                res.extend(data)
        return res

    def collect_observe_entities(self, timestamp: float = None) -> Dict[str, List[DataRecord]]:
        """
        采集所有观测对象的实例数据。
        例：
        输入：timestamp = 0,
             observe_meta = {
                 "tcp_link": ObserveMeta(type="tcp_link", metrics=["rx_bytes", "tx_bytes"]),
                 "task": ObserveMeta(type="task", metrics=["fork_count"])
             }
        输出：res = {
                 "tcp_link": [
                     DataRecord(metric_id="xxx_tcp_link_rx_bytes", timestamp=0, metric_value=1,
                                labels=[Label(name="machine_id", value="machine1")]),
                     DataRecord(metric_id="xxx_tcp_link_tx_bytes", timestamp=0, metric_value=2,
                                labels=[Label(name="machine_id", value="machine1")]),
                 ],
                 "task": [
                     DataRecord(metric_id="xxx_task_fork_count", timestamp=0, metric_value=1,
                                labels=[Label(name="machine_id", value="machine1")]),
                 ]
             }
        @param timestamp: 采集的时间戳
        @return: 所有观测对象在给定时间戳的所有实例数据
        """
        res = {}
        timestamp = time.time() if timestamp is None else timestamp
        for type_, observe_meta in ObserveMetaMgt().observe_meta_map.items():
            data = self.collect_observe_entity(observe_meta, timestamp)
            if len(data) > 0:
                res[type_] = data
        return res

    def aggregate_entities_by_label(self, observe_entities: Dict[str, List[DataRecord]]) -> Dict[str, List[dict]]:
        """
        将属于同一个观测实例的多个不同指标的数据记录聚合为一条实例数据。
        例：
        输入：observe_entities = {
                 "tcp_link": [
                     DataRecord(metric_id="xxx_tcp_link_rx_bytes", timestamp=0, metric_value=1,
                                labels=[Label(name="machine_id", value="machine1")]),
                     DataRecord(metric_id="xxx_tcp_link_rx_bytes", timestamp=0, metric_value=2,
                                labels=[Label(name="machine_id", value="machine2")]),
                     DataRecord(metric_id="xxx_tcp_link_tx_bytes", timestamp=0, metric_value=3,
                                labels=[Label(name="machine_id", value="machine1")]),
                     DataRecord(metric_id="xxx_tcp_link_tx_bytes", timestamp=0, metric_value=4,
                                labels=[Label(name="machine_id", value="machine2")]),
                 ],
             }
        输出：res = {
                 "tcp_link": [
                     {rx_bytes: 1, tx_bytes: 3, timestamp: 0, machine_id: "machine1"},
                     {rx_bytes: 2, tx_bytes: 4, timestamp: 0, machine_id: "machine2"},
                 ]
             }
        @param observe_entities: 聚合之前的观测实例数据
        @return: 聚合之后的观测实例数据，每条观测实例数据为 <key:value> 对的字典形式
        """
        res = {}

        for entity_type, entity_records in observe_entities.items():
            label_map = {}
            entity_keys = ObserveMetaMgt().get_observe_meta(entity_type).keys
            for record in entity_records:
                _filter_keys = _filter_unique_labels(record.labels, entity_keys)
                ok, _id = _id_of_keys(_filter_keys, entity_keys)
                if not ok:
                    logger.logger.debug("Data error: required key of observe type {} miss.".format(entity_type))
                    continue
                if _id not in label_map:
                    item = {}
                    item.setdefault("timestamp", record.timestamp)
                    for label in record.labels:
                        item.setdefault(label.name, label.value)
                    label_map.setdefault(_id, item)
                metric_name = self._get_metric_name(record.metric_id, entity_type)
                label_map.get(_id).setdefault(metric_name, record.metric_value)
            if len(label_map) > 0:
                res[entity_type] = list(label_map.values())

        return res

    def get_observe_entities(self, timestamp: float = None) -> List[ObserveEntity]:
        """
        获取所有的观测实例数据，并作为统一数据模型返回。
        例：
        输入：timestamp = 0
        输出：res = [
                 ObserveEntity(id="TCP_LINK_machine1", type="tcp_link", timestamp=0,
                               attrs={rx_bytes: 1, tx_bytes: 2, machine_id: "machine1"}),
                 ObserveEntity(id="TCP_LINK_machine2", type="tcp_link", timestamp=0,
                               attrs={rx_bytes: 3, tx_bytes: 4, machine_id: "machine2"}),
                 ObserveEntity(id="TASK_machine1", type="task", timestamp=0,
                               attrs={fork_count: 1, machine_id: "machine1"}),
             ]
        @param timestamp: 观测实例数据对应的时间戳
        @return: 所有的观测实例数据，以 List[ObserveEntity] 的形式返回。
        """
        res = []

        raw_entities = self.collect_observe_entities(timestamp)
        aggr_entities = self.aggregate_entities_by_label(raw_entities)
        for entity_type, one_type_entities in aggr_entities.items():
            if not one_type_entities:
                continue

            entity_meta = ObserveMetaMgt().get_observe_meta(entity_type)
            for entity_data in one_type_entities:
                entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_data, entity_meta)
                if entity is not None:
                    res.append(entity)

        logical_entities = ObserveEntityCreator.create_logical_observe_entities(res)
        res.extend(logical_entities)

        return res

    def _get_metric_id(self, entity_type: str, metric_name: str):
        return "{}_{}_{}".format(ObserveMetaMgt().data_agent, entity_type, metric_name)

    def _get_metric_name(self, metric_id: str, entity_name: str) -> str:
        start = len("{}_{}_".format(ObserveMetaMgt().data_agent, entity_name))
        return metric_id[start:len(metric_id)]
