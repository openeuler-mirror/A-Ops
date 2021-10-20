import time
from spider.data_process.data_to_entity import node_entity_process
from anomaly_detection.anomaly_detection_base_on_threshold import threshold_based_anomaly_detection
from anomaly_detection.common import CONF_INFO, g_edges_list, EDGES_LIST_UPDATE_INTERVAL, ANOMALY_DETECTION_MODEL_TYPE

DETECTION_FUNC = {ANOMALY_DETECTION_MODEL_TYPE.THRESHOLD_MODEL: threshold_based_anomaly_detection}

def edges_infos_detection(conf_info, edges_infos):
    """
    对edges_infos进行遍历检测
    :param edges_infos:
        {('1.1.1.1', '0.0.0.0', '1234', 'xx.yy'): {'rx_bytes': '3613', 'tx_bytes': '1590415'},
         ('1.1.1.1', '0.0.0.0', '1234', 'xx.zz'): {'rx_bytes': '3613', 'tx_bytes': '1590415'}}
    :return:
        原始基础上增加anomaly_infos字段
        {('1.1.1.1', '0.0.0.0', '1234', 'xx.yy'): {'rx_bytes': '3613', 'tx_bytes': '1590415', "anomaly_infos":[{"anomaly_attr":"", "anomaly_type":""}, ...]},
         ('1.1.1.1', '0.0.0.0', '1234', 'xx.zz'): {'rx_bytes': '3613', 'tx_bytes': '1590415', "anomaly_infos":[{"anomaly_attr":"", "anomaly_type":""}, ...]}}
    """
    result = {}
    # 入参校验
    if not edges_infos or not conf_info:
        return result

    for edges in edges_infos:
        result[edges] = edges_infos.get(edges)

        # 解析机器、对象信息
        machine_name = edges[3].split(".")[0]
        item_name = edges[3].split(".")[1]
        if not machine_name or not item_name:
            continue

        # 获取检测函数
        detection_info = conf_info.get("tcp_link")
        if not detection_info:
            continue

        model_type = detection_info.get("model_info", {}).get("type")
        if not model_type or model_type == 0:
            continue
        else:
            detection_func = DETECTION_FUNC.get(str(model_type))

        # 构建检测函数入参
        machine_info = {"machine_name":machine_name, "item_name":item_name}
        detection_data = edges_infos.get(edges)

        # 检测及结果
        detection_result = detection_func(machine_info, detection_data)
        result[edges].setdefault("anomaly_infos", detection_result)

    return result

def update_edges_info(edges_table, timestamp):
    """
    更新tcp_link基线
    :param edges_table: 当前link信息
    :param timestamp:   时间戳
    :return:
    """
    edges_list = {}
    for edge, edge_info in edges_table.items():
        if edge_info.get("0") and edge_info.get("1"):
            edges_list[edge] = edge_info

    g_edges_list["edges_list"] = edges_list
    g_edges_list["timestamp"] = timestamp
    return


def edges_table_detection(edges_table, timestamp):
    """
    检测tcp-link是否缺失
    :param edges_table: dict, 当前所有的link集合，例如：
                        {('0.0.0.0', '1.1.1.1', '8080', 'vm1.xxx.123'): {'1': {'h': 'xxx', 'p': 'yyy'},
                         ('0.0.0.0', '1.1.1.1', '8080', 'vm1.xxx.123'): {'1': {'h': 'xxx', 'p': 'yyy'}}
    :param timestamp: 时间戳
    :return: dict, 在原始边数据上增加status字段，[0:缺失，1:正常]， 例如：
                        {('0.0.0.0', '1.1.1.1', '8080', 'vm1.xxx.123'): {'1': {'h': 'xxx', 'p': 'yyy'}, "status": 0},
                         ('0.0.0.0', '1.1.1.1', '8080', 'vm1.xxx.123'): {'1': {'h': 'xxx', 'p': 'yyy'}, "status": 1}}
    """
    result = {}

    # 入参校验
    if not edges_table:
        return result

    # 拼装返回值
    for edge in edges_table:
        result[edge] = edges_table.get(edge)
        result[edge].setdefault("status", 1)

    # 检查基线
    g_edges_list_timestamp = g_edges_list.get("timestamp")
    if (int(timestamp) - int(g_edges_list_timestamp)) >= EDGES_LIST_UPDATE_INTERVAL:
        update_edges_info(edges_table, timestamp)
        return result

    # 检查edges_table
    _edges_list = [edge for edge in edges_table.keys()]
    print("_edges_list", _edges_list)
    for edge in g_edges_list.get("edges_list", {}).keys():
        if edge not in _edges_list:
            result[edge] = g_edges_list.get("edges_list", {}).get(edge)
            result[edge]["status"] = 0

    return result


def detection(edges_table, edges_infos, nodes_table, lb_tables, vm_table):
    timestamp = int(time.time())

    _edges_table = edges_table_detection(edges_table, timestamp)
    _edges_infos = edges_infos_detection(CONF_INFO, edges_infos)

    return _edges_table, _edges_infos, nodes_table, lb_tables, vm_table







