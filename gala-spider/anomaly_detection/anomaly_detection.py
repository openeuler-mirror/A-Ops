import time
from typing import Dict
from dataclasses import asdict

from anomaly_detection.attribute_detection_base_on_threshold import threshold_based_anomaly_detection
from anomaly_detection.item_detection import tcp_link_item_detection, node_item_detection, lb_item_detection, vm_item_detection
from anomaly_detection.util import OBJECT_TYPE, ANOMALY_DETECTION_MODEL_TYPE
from spider.data_process.models import TcpLinkKey, TcpLinkInfo
from spider.util.conf import anomaly_detection_conf


DETECTION_FUNC = {ANOMALY_DETECTION_MODEL_TYPE.EXPERT_MODEL: threshold_based_anomaly_detection}


def attribute_detection(object_attr_data, anomaly_detection_conf):
    """
    attribute detection
    :param object_attr_data:
        dict, example:
        {"tcp_link": {
            TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613', tx_bytes='3304039'...),...),
            TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613', tx_bytes='3304039'...),...),
            }
         "process":{}
        }
    :return:
        Only abnormal links are returned. The key remains unchanged, and value is {link_metric, anomaly_infos}.
    """
    result = {}

    if not object_attr_data or not anomaly_detection_conf:
        return result

    _tcp_link_data = object_attr_data.get(OBJECT_TYPE.TCP_LINK)
    if not _tcp_link_data:
        return result
    else:
        _result = {}

    for tcp_link_key, tcp_link_info in _tcp_link_data.items():
        if tcp_link_info.link_metric is None:
            continue

        c_process = tcp_link_info.key.c_process
        machine_name = c_process.host.host_name
        item_name = c_process.process_name
        if not machine_name or not item_name:
            continue

        tcp_link_detection_conf = anomaly_detection_conf.get(OBJECT_TYPE.TCP_LINK)
        if not tcp_link_detection_conf:
            continue
        detection_model_type = tcp_link_detection_conf.get("detection_model_type")
        if not detection_model_type:
            continue
        else:
            detection_func = DETECTION_FUNC.get(str(detection_model_type))

        object_base_info = {"machine_name": machine_name,
                            "object_type": OBJECT_TYPE.TCP_LINK,
                            "item_name": item_name}
        detection_data = asdict(tcp_link_info.link_metric)

        detection_result = detection_func(object_base_info, detection_data)
        if detection_result:
            _result[tcp_link_key] = detection_data
            _result[tcp_link_key].setdefault("anomaly_infos", detection_result)
        else:
            continue

    result[OBJECT_TYPE.TCP_LINK] = _result
    return result

def item_detection(object_item_data: Dict[TcpLinkKey, TcpLinkInfo], timestamp) -> Dict[TcpLinkKey, TcpLinkInfo]:
    """
    Detect whether the observation object is missing
    :param object_item_data:
        Data to be detected, dict, example:
        {"tcp_link": {TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), ..., status=1),
                      TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), ..., status=1)}
         "nodes": proc_nodes_table,
         "lb": lb_table,
         "vm": vm_table
        }
    :param timestamp: Data collection time
    """
    result = {}

    if not object_item_data or not timestamp:
        print("item_detection error 1")
        return object_item_data

    _tcp_link_items = object_item_data.get(OBJECT_TYPE.TCP_LINK)
    if _tcp_link_items:
        tcp_link_item = tcp_link_item_detection(_tcp_link_items, timestamp)
        result[OBJECT_TYPE.TCP_LINK] = tcp_link_item

    _node_items = object_item_data.get(OBJECT_TYPE.NODES)
    if _node_items:
        node_items = node_item_detection(_node_items, timestamp)
        result[OBJECT_TYPE.NODES] = node_items

    _lb_items = object_item_data.get(OBJECT_TYPE.LB)
    if _lb_items:
        lb_items = lb_item_detection(_lb_items, timestamp)
        result[OBJECT_TYPE.LB] = lb_items

    _vm_items = object_item_data.get(OBJECT_TYPE.VM)
    if _vm_items:
        vm_items = vm_item_detection(_vm_items, timestamp)
        result[OBJECT_TYPE.LB] = vm_items

    return result

def detection(object_item_data, object_attr_data):
    print("4、enter detection")
    timestamp = int(time.time())
    _object_item_data = item_detection(object_item_data, timestamp)
    _object_attr_data = attribute_detection(object_attr_data, anomaly_detection_conf)

    return _object_item_data, _object_attr_data






