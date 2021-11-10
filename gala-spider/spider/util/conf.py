import os
import yaml

CONFIG_PATH = "/opt/gala-spider/gala-spider.yaml"

def get_conf_info(path):
    result = {}

    true_path = os.path.realpath(path)
    try:
        with open(true_path, "rb") as f:
            result = yaml.safe_load(f.read())
    except IOError:
        print("Invalid file")

    return result

CONF_INFO = get_conf_info(CONFIG_PATH)

db_agent = CONF_INFO.get("global", {}).get("data_source")
ui_agent = CONF_INFO.get("global", {}).get("ui_source")

kafka_topic = CONF_INFO.get("kafka", {}).get("topic")
kafka_broker = CONF_INFO.get("kafka", {}).get("broker")
kafka_group_id = CONF_INFO.get("kafka", {}).get("group_id")

prometheus_server = CONF_INFO.get("prometheus", {}).get("SERVER", "")
prometheus_port = CONF_INFO.get("prometheus", {}).get("PORT", "")
prometheus_range_query_api = CONF_INFO.get("prometheus", {}).get("RANGE_QUERY_API", "")
prometheus_instance_query_api = CONF_INFO.get("prometheus", {}).get("INSTANT_QUERY_API", "")

prometheus_range_query_url = "{server}:{port}{api}".format(server=prometheus_server,
                                                           port=prometheus_port,
                                                           api=prometheus_range_query_api)
prometheus_instance_query_url = "{server}:{port}{api}".format(server=prometheus_server,
                                                              port=prometheus_port,
                                                              api=prometheus_instance_query_api)

neo4j_addr = CONF_INFO.get("neo4j", {}).get("address")
neo4j_uname = CONF_INFO.get("neo4j", {}).get("username")
neo4j_pwd = str(CONF_INFO.get("neo4j", {}).get("password"))
neo4j_timer = CONF_INFO.get("neo4j", {}).get("timer")

base_table = CONF_INFO.get("table_info", {}).get("base_table_name")
other_table = CONF_INFO.get("table_info", {}).get("other_table_name")
exclude_ip = CONF_INFO.get("option", {}).get("exclude_addr")

temp_tcp_file = CONF_INFO.get("temp_path", {}).get("temp_tcp_file")
temp_other_file = CONF_INFO.get("temp_path", {}).get("temp_other_file")

spider_port = CONF_INFO.get("spider", {}).get("port")

anomaly_detection_conf = CONF_INFO.get("anomaly_detection", {})

prometheus_conf = {
    "base_url": CONF_INFO.get("prometheus", {}).get("base_url"),
    "instant_api": CONF_INFO.get("prometheus", {}).get("instant_api"),
    "range_api": CONF_INFO.get("prometheus", {}).get("range_api"),
    "step": CONF_INFO.get("prometheus", {}).get("step")
}
