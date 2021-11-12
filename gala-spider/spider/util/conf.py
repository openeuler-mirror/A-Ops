import os
import configparser

CONFIG = "/etc/spider/gala-spider.conf"

# analysis configuration
cf = configparser.ConfigParser()
if os.path.exists(CONFIG):
    cf.read(CONFIG, encoding="utf-8")
else:
    cf.read("config/gala-spider.conf", encoding="utf-8")

db_agent = cf.get("global", "data_source")
ui_agent = cf.get("global", "ui_source")
observe_conf_path = cf.get("global", "observe_conf_path")

kafka_topic = cf.get("kafka", "topic")
kafka_broker = cf.get("kafka", "broker")

neo4j_addr = cf.get("neo4j", "address")
neo4j_uname = cf.get("neo4j", "username")
neo4j_pwd = cf.get("neo4j", "password")
neo4j_timer = cf.get("neo4j", "timer")

base_table = cf.get("table_info", "base_table_name")
other_table = cf.get("table_info", "other_table_name")
exclude_ip = cf.get("option", "exclude_addr")

temp_tcp_file = cf.get("temp_path", "temp_tcp_file")
temp_other_file = cf.get("temp_path", "temp_other_file")

spider_port = cf.get("spider", "port")

conf_path = cf.get("anomaly_detection", "config_path")

# prometheus config
prometheus_conf = {
    "base_url": cf.get("prometheus", "base_url"),
    "instant_api": cf.get("prometheus", "instant_api"),
    "range_api": cf.get("prometheus", "range_api"),
    "step": cf.get("prometheus", "step")
}
