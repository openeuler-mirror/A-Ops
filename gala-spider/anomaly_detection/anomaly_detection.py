import time
from typing import Dict
from dataclasses import asdict

from anomaly_detection.attribute_detection_base_on_threshold import threshold_based_anomaly_detection
from anomaly_detection.item_detection import tcp_link_item_detection, node_item_detection, lb_item_detection, vm_item_detection
from anomaly_detection.util import EntityName, AnomalyDetectionModelType, get_tcp_link_label_info
from spider.data_process.models import TcpLinkKey, TcpLinkInfo
from spider.util.conf import anomaly_detection_conf


DETECTION_FUNC = {AnomalyDetectionModelType.EXPERT_MODEL: threshold_based_anomaly_detection}


def tcp_link_attr_detection(timestamp, tcp_link_data):
    """
    :param timestamp: 1234567890
    :param tcp_link_data:
        {TcpLinkKey(s_ip="", s_port="",...):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613',...),link_type='tcp_link', status=1),
         TcpLinkKey(s_ip="", s_port="",...):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613',...),link_type='tcp_link', status=1),}
    :return:
        {TcpLinkKey(s_ip='', s_port="",...): {'rx_bytes': '6200', ..., 'anomaly_infos': [{'anomaly_attr': 'rtt', 'anomaly_type': 'ABOVE THRESHOLD'}]},
         TcpLinkKey(s_ip='', s_port="",...): {'rx_bytes': '1234', ..., 'anomaly_infos': [{'anomaly_attr': 'rtt', 'anomaly_type': 'ABOVE THRESHOLD'}]}}
    """
    result = {}

    if not timestamp or not tcp_link_data:
        return result

    # get user conf
    tcp_link_detection_conf = anomaly_detection_conf.get(EntityName.TCP_LINK)
    if not tcp_link_detection_conf:
        return result

    for tcp_link_key, tcp_link_info in tcp_link_data.items():
        if tcp_link_info.link_metric is None:
            continue

        # get detection func
        detection_model_type = tcp_link_detection_conf.get("detection_model_type")
        if not detection_model_type:
            continue
        else:
            detection_func = DETECTION_FUNC.get(str(detection_model_type))

        # get label info
        label_info = get_tcp_link_label_info(tcp_link_key)
        if not label_info:
            continue

        entity_base_info = {"timestamp": timestamp,
                            "entity_name": EntityName.TCP_LINK,
                            "label_info": label_info}

        detection_data = asdict(tcp_link_info.link_metric)

        # detection
        detection_result = detection_func(entity_base_info, detection_data)
        if detection_result:
            result[tcp_link_key] = detection_data
            result[tcp_link_key].setdefault("anomaly_infos", detection_result)
        else:
            continue

    return result


def attribute_detection(timestamp, entity_attr_data, anomaly_detection_conf):
    """
    :param entity_attr_data:
        {"tcp_link": {
            TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613', tx_bytes='3304039'...),...),
            TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), link_metric=TcpLinkMetric(rx_bytes='3613', tx_bytes='3304039'...),...),
            }
         "nginx_link":{}
        }

    :return:
        {"tcp_link":{
            TcpLinkKey(s_ip="",...):{'rx_bytes': '6200', ..., 'anomaly_infos': [{'anomaly_attr': 'rtt', 'anomaly_type': 'ABOVE THRESHOLD'}]},
            TcpLinkKey(s_ip="",...):{'rx_bytes': '6200', ..., 'anomaly_infos': [{'anomaly_attr': 'rtt', 'anomaly_type': 'ABOVE THRESHOLD'}]}
            }
         "nginx_link":{}
        }
    """
    result = {}

    if not timestamp or not entity_attr_data or not anomaly_detection_conf:
        return result

    # tcp_link attr detection
    _tcp_link_data = entity_attr_data.get(EntityName.TCP_LINK)
    if _tcp_link_data:
        result[EntityName.TCP_LINK] = tcp_link_attr_detection(timestamp, _tcp_link_data)

    return result


def item_detection(entity_item_data: Dict[TcpLinkKey, TcpLinkInfo], timestamp) -> Dict[TcpLinkKey, TcpLinkInfo]:
    """
    Check whether the entity object is missing.
    Update the status field [0: missing; 1: normal].
    Now, only the tcp_link is checked.

    :param entity_item_data:
        {"tcp_link": {TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), ..., status=1),
                      TcpLinkKey(s_ip="", s_port="", c_ip="", c_process=""):TcpLinkInfo(key=(), ..., status=1)}
         "nodes": proc_nodes_table,
         "lb": lb_table,
         "vm": vm_table
        }
    :param timestamp:
    """
    result = {}

    if not entity_item_data or not timestamp:
        print("item_detection error: Missing detection data.\n")
        return entity_item_data

    # tcp_link
    _tcp_link_items = entity_item_data.get(EntityName.TCP_LINK)
    if _tcp_link_items:
        tcp_link_item = tcp_link_item_detection(_tcp_link_items, timestamp)
        result[EntityName.TCP_LINK] = tcp_link_item

    # nodes
    _node_items = entity_item_data.get(EntityName.NODES)
    if _node_items:
        node_items = node_item_detection(_node_items, timestamp)
        result[EntityName.NODES] = node_items

    # lb
    _lb_items = entity_item_data.get(EntityName.LB)
    if _lb_items:
        lb_items = lb_item_detection(_lb_items, timestamp)
        result[EntityName.LB] = lb_items

    # vm
    _vm_items = entity_item_data.get(EntityName.VM)
    if _vm_items:
        vm_items = vm_item_detection(_vm_items, timestamp)
        result[EntityName.LB] = vm_items

    return result


def detection(timestamp, entity_item_data, entity_attr_data):
    _entity_item_data = item_detection(entity_item_data, timestamp)
    _entity_attr_data = attribute_detection(timestamp, entity_attr_data, anomaly_detection_conf)

    return _entity_item_data, _entity_attr_data
