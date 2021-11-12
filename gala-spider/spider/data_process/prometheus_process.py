import yaml
from typing import List, Dict
import time

from spider.util.conf import observe_conf_path
from spider.collector.data_collector import DataRecord, Label
from spider.collector.prometheus_collector import g_prometheus_collector


def resolve_observe_conf(conf_path: str) -> dict:
    data = {}

    try:
        with open(conf_path, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except IOError as ex:
        print("Unable to open observe config file: {}".format(ex))

    return data


def _filter_unique_labels(labels: List[Label]) -> List[Label]:
    res = []

    for label in labels:
        if label.name == '__name__' or label.name == 'instance':
            continue
        res.append(label)

    return res


def _id_of_labels(labels: List[Label]) -> tuple:
    tmp = [(label.name, label.value) for label in labels]
    return tuple(tmp)


class PrometheusProcessor:
    def __init__(self, conf_path: str):
        _observe_meta_info = resolve_observe_conf(conf_path)
        self.data_agent = _observe_meta_info.get("data_agent")
        self.observe_entities = _observe_meta_info.get("observe_entities", {})

    def collect_observe_entity(self, entity: dict, timestamp: float = None) -> List[DataRecord]:
        res = []
        timestamp = time.time() if timestamp is None else timestamp
        for metric in entity.get("metrics"):
            metric_id = "{}_{}_{}".format(self.data_agent, entity.get("name"), metric)
            data = g_prometheus_collector.get_instant_data(metric_id, timestamp)
            if len(data) > 0:
                res.extend(data)
        return res

    def collect_observe_entities(self, timestamp: float = None) -> Dict[str, List[DataRecord]]:
        res = {}
        timestamp = time.time() if timestamp is None else timestamp
        for entity in self.observe_entities:
            data = self.collect_observe_entity(entity, timestamp)
            if len(data) > 0:
                res[entity.get("name")] = data
        return res

    def aggregate_entities_by_label(self, observe_entities: Dict[str, List[DataRecord]]) -> Dict[str, list]:
        res = {}

        for entity_name, entity_records in observe_entities.items():
            label_map = {}
            for record in entity_records:
                _filter_labels = _filter_unique_labels(record.labels)
                _id = _id_of_labels(_filter_labels)
                if _id not in label_map:
                    item = {}
                    item.setdefault("timestamp", record.timestamp)
                    for label in _filter_labels:
                        item.setdefault(label.name, label.value)
                    item.setdefault("entity_name", entity_name)

                    # TODO : to delete after gopher reports complete labels
                    item.setdefault("table_name", entity_name)
                    item.setdefault("hostname", "xxx")

                    label_map.setdefault(_id, item)
                metric_name = self._get_metric_name(record.metric_id, entity_name)
                label_map.get(_id).setdefault(metric_name, record.metric_value)
            if len(label_map) > 0:
                res[entity_name] = list(label_map.values())

        return res

    def get_observe_entities(self, timestamp: float = None) -> List[dict]:
        res = []

        raw_entities = self.collect_observe_entities(timestamp)
        aggr_entities = self.aggregate_entities_by_label(raw_entities)
        for entity_name, one_type_entities in aggr_entities.items():
            if not one_type_entities:
                continue
            res.extend(one_type_entities)

        return res

    def _get_metric_name(self, metric_id: str, entity_name: str) -> str:
        start = len("{}_{}_".format(self.data_agent, entity_name))
        return metric_id[start:len(metric_id)]


g_prometheus_processor = PrometheusProcessor(observe_conf_path)

# TODO: delete
if __name__ == '__main__':
    import json
    _res = g_prometheus_processor.get_observe_entities()
    print(json.dumps(_res, indent=4))
