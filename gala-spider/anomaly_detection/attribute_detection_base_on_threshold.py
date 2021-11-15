import ast
from spider.util.conf import anomaly_detection_conf
from anomaly_detection.util import ATTR_ANOMALY_TYPE


def threshold_based_anomaly_detection(object_base_info, detection_data):
    """
    threshold based anomaly detection
    :param:
        object_base_info:
            dict, basic information of observation object, example:{"machine_name":"exe", "object_type": "tcp_link", "item_name":"ffmpeg1"}
        detection_data:
            dict, data to be detected, example: {'rx_bytes': '123', 'tx_bytes': '123'}
    :return:
        dict, [{"anomaly_attr":"", "anomaly_type":""},{"anomaly_attr":"", "anomaly_type":""}...]
    """
    result = []

    if not object_base_info or not detection_data:
        return result

    machine_name = object_base_info.get("machine_name")
    item_name = object_base_info.get("item_name")
    object_type = object_base_info.get("object_type")
    if not machine_name or not item_name or not object_type:
        return result

    # Get model parameters (threshold information)
    this_threshold_info = anomaly_detection_conf.get(object_type, {}).get("detection_attributes")
    if not this_threshold_info:
        return result

    for attr in this_threshold_info:
        attr_val = ast.literal_eval(str(detection_data.get(attr)))
        if not attr_val:
            continue

        _threshold = ast.literal_eval(str(this_threshold_info.get(attr).get("threshold")))
        _model = this_threshold_info.get(attr).get("method")
        if not _threshold or not _model:
            continue

        # detection
        if _model == ">":
            if attr_val > _threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": ATTR_ANOMALY_TYPE.ABOVE_THRESHOLD})
        elif _model == ">=":
            if attr_val >= _threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": ATTR_ANOMALY_TYPE.ABOVE_THRESHOLD})
        elif _model == "<":
            if attr_val > _threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": ATTR_ANOMALY_TYPE.BELOW_THRESHOLD})
        elif _model == "<=":
            if attr_val >= _threshold:
                result.append({"anomaly_attr": attr, "anomaly_type": ATTR_ANOMALY_TYPE.BELOW_THRESHOLD})
        else:
            continue

    return result