import ast
from spider.util.conf import anomaly_detection_conf
from anomaly_detection.util import AttrAnomalyType, get_instant_data


def threshold_based_anomaly_detection(entity_base_info, detection_data):
    """
    :param entity_base_info: 
        example: {"timestamp": timestamp,
                  "entity_name": EntityName.TCP_LINK,
                  "label_info": {"server_ip"="", 
                                 "server_port"="",
                                 "client_ip"="",
                                 "process_name"=""}}

    :param detection_data:
        example: {rx_bytes='3613', tx_bytes='3304039'...}
    :return: 
        example: [{'anomaly_attr': 'rx_bytes', 'anomaly_type': 'ABOVE THRESHOLD'},
                  {'anomaly_attr': 'tx_bytes', 'anomaly_type': 'ABOVE THRESHOLD'}]
    """
    result = []

    if not entity_base_info or not detection_data:
        return result

    timestamp = entity_base_info.get("timestamp")
    entity_name = entity_base_info.get("entity_name")
    label_info = entity_base_info.get("label_info")
    if not entity_name or not timestamp:
        return result

    this_threshold_info = anomaly_detection_conf.get(entity_name, {}).get("detection_attributes")
    if not this_threshold_info:
        return result

    # detection
    for attr in this_threshold_info:
        _attr_val = detection_data.get(attr)
        if _attr_val == "":
            continue
        attr_val = ast.literal_eval(_attr_val)

        entity_info = {"entity_name": entity_name, "metric_name": attr}
        _timestamp = timestamp - this_threshold_info.get(attr).get("detection_interval", 5)
        _old_attr_val = get_instant_data(entity_info, label_info, _timestamp)
        if _old_attr_val == "":
            continue
        old_attr_val = ast.literal_eval(_old_attr_val)
        attr_increment = attr_val - old_attr_val

        threshold = this_threshold_info.get(attr).get("threshold")
        if threshold is None:
            continue

        model = this_threshold_info.get(attr).get("method")
        if model is None:
            continue

        if model == ">":
            if attr_increment > threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": AttrAnomalyType.ABOVE_THRESHOLD})
        elif model == ">=":
            if attr_increment >= threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": AttrAnomalyType.ABOVE_THRESHOLD})
        elif model == "<":
            if attr_increment > threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": AttrAnomalyType.BELOW_THRESHOLD})
        elif model == "<=":
            if attr_increment >= threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": AttrAnomalyType.BELOW_THRESHOLD})
        else:
            continue

    return result
