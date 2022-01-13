import os

from spider.conf import SpiderConfig
from spider.collector.data_collector import DataRecord
from spider.conf.observe_meta import ObserveMeta, ObserveMetaMgt
from spider.entity_mgt import ObserveEntityCreator
from spider.entity_mgt.models import ObserveEntity


def assert_data_record(record: DataRecord, record_dict: dict):
    metric = record_dict.get("metric")
    value = record_dict.get("value")
    assert record.metric_id == metric.get("__name__")
    assert record.timestamp == value[0]
    assert record.metric_value == value[1]
    for label in record.labels:
        assert label.value == metric.get(label.name)


def assert_observe_entity(entity: ObserveEntity, expect_entity: ObserveEntity):
    assert entity.id == expect_entity.id
    assert entity.type == expect_entity.type
    assert entity.name == expect_entity.name
    assert entity.level == expect_entity.level
    assert entity.timestamp == expect_entity.timestamp
    assert entity.attrs == expect_entity.attrs


def gen_instant_resp_data():
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": []
        }
    }


def append_metric_items(resp_data: dict, metric_items: list):
    for metric_item in metric_items:
        resp_data.get("data").get("result").append(metric_item)


def gen_task_metric_item(metric_name, **kwargs):
    metric = {
        "__name__": "gala_gopher_task_{}".format(metric_name),
        "pid": kwargs.get('pid') or 1,
        "task_name": kwargs.get('task_name') or "task0",
        "machine_id": kwargs.get('machine_id') or "machine0"
    }
    value = [kwargs.get('timestamp') or 0, 1]

    return {'metric': metric, 'value': value}


def gen_tcp_link_metric_item(metric_name, **kwargs):
    metric = {
        "__name__": "gala_gopher_tcp_link_{}".format(metric_name),
        "server_ip": kwargs.get('server_ip') or "0.0.0.0",
        "server_port": kwargs.get('server_port') or "80",
        "client_ip": kwargs.get('client_ip') or "0.0.0.0",
        "client_port": kwargs.get('client_port') or "90",
        "pid": kwargs.get('pid') or 1,
        "machine_id": kwargs.get('machine_id') or "machine0",
        "role": kwargs.get('role') or 0
    }
    value = [kwargs.get('timestamp') or 0, 1]

    return {'metric': metric, 'value': value}


def gen_host_entity(observe_meta: ObserveMeta, machine_id='123', **kwargs) -> ObserveEntity:
    entity_type = 'host'
    entity_data = {
        'machine_id': machine_id,
        'hostname': kwargs.get('hostname') or 'machine0',
        'timestamp': kwargs.get('timestamp') or 0,
    }
    return ObserveEntityCreator.create_observe_entity(entity_type, entity_data, observe_meta)


def gen_task_entity(observe_meta: ObserveMeta, pid=1, machine_id='123', **kwargs) -> ObserveEntity:
    entity_type = 'task'
    entity_data = {
        'pid': pid,
        'machine_id': machine_id,
        'task_name': kwargs.get('task_name') or 'task0',
        'container_id': kwargs.get('container_id') or None,
        'fork_count': kwargs.get('fork_count') or 0,
        'timestamp': kwargs.get('timestamp') or 0,
    }
    return ObserveEntityCreator.create_observe_entity(entity_type, entity_data, observe_meta)


def gen_tcp_link_entity(observe_meta: ObserveMeta, server_ip='0.0.0.0', server_port='80',
                        client_ip='1.1.1.1', pid=1, machine_id='123', **kwargs) -> ObserveEntity:
    entity_type = 'tcp_link'
    entity_data = {
        "server_ip": server_ip,
        "server_port": server_port,
        "client_ip": client_ip,
        "pid": pid,
        "machine_id": machine_id,
        "role": kwargs.get('role') or 0,
        "rx_bytes": kwargs.get('rx_bytes') or 0,
        "tx_bytes": kwargs.get('tx_bytes') or 0,
        'timestamp': kwargs.get('timestamp') or 0,
    }
    return ObserveEntityCreator.create_observe_entity(entity_type, entity_data, observe_meta)


def gen_ipvs_link_entity(observe_meta: ObserveMeta, server_ip='0.0.0.0', server_port='80',
                         virtual_ip='0.0.0.0', virtual_port='80', local_ip='2.2.2.2',
                         client_ip='1.1.1.1', pid=1, machine_id='123', **kwargs) -> ObserveEntity:
    entity_type = 'ipvs_link'
    entity_data = {
        "server_ip": server_ip,
        "server_port": server_port,
        "virtual_ip": virtual_ip,
        "virtual_port": virtual_port,
        "local_ip": local_ip,
        "client_ip": client_ip,
        "pid": pid,
        "machine_id": machine_id,
        "protocol": kwargs.get('protocol') or 0,
        "link_count": kwargs.get('link_count') or 0,
        'timestamp': kwargs.get('timestamp') or 0,
    }
    return ObserveEntityCreator.create_observe_entity(entity_type, entity_data, observe_meta)


def init_spider_config():
    cur_file_path, _ = os.path.split(os.path.abspath(__file__))
    spider_config = SpiderConfig()
    spider_config.load_from_yaml(cur_file_path + "./static/tmp_gala_spider.yaml")
    return spider_config


def init_observe_meta_mgt():
    cur_file_path, _ = os.path.split(os.path.abspath(__file__))
    observe_meta_mgt = ObserveMetaMgt()
    observe_meta_mgt.load_from_yaml(cur_file_path + "./static/tmp_observe.yaml")
    assert len(observe_meta_mgt.observe_meta_map) > 0
    return observe_meta_mgt
