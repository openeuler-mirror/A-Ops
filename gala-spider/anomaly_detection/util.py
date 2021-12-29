from spider.collector.prometheus_collector import g_prometheus_collector
from spider.util.conf import db_agent


class AnomalyDetectionModelType:
    EXPERT_MODEL = "EXPERT_MODEL"
    AI_MODEL = "AI_MODEL"


class AttrAnomalyType:
    BELOW_THRESHOLD = "BELOW THRESHOLD"
    ABOVE_THRESHOLD = "ABOVE THRESHOLD"


class EntityName:
    TCP_LINK = "tcp_link"
    NODES = "nodes"
    LB = "lb"
    VM = "vm"


class AnomalyStatus:
    ANOMALY_NO = "ANOMALY_NO"
    ANOMALY_YES = "ANOMALY_YES"
    ANOMALY_LACKING = "ANOMALY_LACKING"

def get_instant_data(entity_info, query_options, timestamp):
    data = ""

    if not entity_info or not timestamp:
        return data

    entity_name = entity_info.get("entity_name")
    metric_name = entity_info.get("metric_name")
    if not entity_name or not metric_name:
        return data

    if db_agent == "prometheus":
        metric_id = "{}_{}_{}".format("gala_gopher", entity_name, metric_name)
        _data = g_prometheus_collector.get_instant_data(metric_id, timestamp, query_options=query_options)
        if not _data:
            return data
        data = _data[0].metric_value
    return data


def get_tcp_link_label_info(tcp_link_key):
    label_info = {}

    label_info.setdefault("server_ip", tcp_link_key.s_ip)
    label_info.setdefault("server_port", tcp_link_key.s_port)
    label_info.setdefault("client_ip", tcp_link_key.c_ip)
    label_info.setdefault("process_name", tcp_link_key.c_process.process_name)
    #label_info.setdefault("host_name", tcp_link_key.c_process.host.host_name)
    return label_info


EDGES_LIST_UPDATE_INTERVAL = 20
g_edges_list = {"timestamp": 0, EntityName.TCP_LINK: {}}


