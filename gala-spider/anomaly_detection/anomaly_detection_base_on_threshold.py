from anomaly_detection.common import CONF_INFO

def threshold_based_anomaly_detection(machine_info, detection_data):
    """
    基于阈值的异常检测，machine_info参数暂时用不到
    :param:
        "machine_info":   dict, 机器及观测对象信息，例如：{"machine_name":"xxx", "item_name":"yyy"},
        "detection_data": dict, 待检测数据，       例如：{'rx_bytes': '123', 'tx_bytes': '123'}
    :return:
        dict, [{"anomaly_attr":"", "anomaly_type":""},{"anomaly_attr":"", "anomaly_type":""}...]
    """
    result = []

    # 入参检验
    if not machine_info or not detection_data:
        return result

    # 解析机器、对象信息
    machine_name = machine_info.get("machine_name")
    item_name = machine_info.get("item_name")
    if not machine_name or not item_name:
        return result
    # print("detecting, machine_name:{}, item_name:{}".format(machine_name, item_name))

    # 获取模型参数——阈值信息
    this_threshold_info = CONF_INFO.get("tcp_link")
    if not this_threshold_info:
        return result

    # 对观测对象的每个属性进行检测
    for i in detection_data:
        _detection_model = this_threshold_info.get(i)
        if not _detection_model:
            continue

        _threshold = int(_detection_model.get("threshold"))
        _model = int(_detection_model.get("model"))

        _detection_result = int(detection_data.get(i)) - int(_threshold)
        if _detection_result * _model >= 0:
            result.append({"anomaly_attr": i, "anomaly_type": str(_model)})
        else:
            continue

    return result