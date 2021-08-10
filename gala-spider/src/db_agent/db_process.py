from kafka import KafkaConsumer
import json
import configparser
import sys
sys.path.append("..")
from lib import util

def db_kafka_agent():
    # obtain temp_files & conf file path
    (find_tcp_path, find_other_path, find_conf_path) = util.get_temp_file_path()
    # analysis configuration
    cf = configparser.ConfigParser()
    cf.read(find_conf_path[0], encoding="utf-8")
    db_agent = cf.get("global", "data_source")
    kafka_topic = cf.get(eval(db_agent), "topic")
    kafka_broker = cf.get(eval(db_agent), "broker")
    base_table = cf.get("table_info", "base_table_name")
    other_table = cf.get("table_info", "other_table_name")
    exclude_ip = cf.get("option", "exclude_addr")
    #print(exclude_ip)
    # can specify a type of IP that isn't recorded
    checkip = eval(exclude_ip)
    # kafka consumer conf
    consumer = KafkaConsumer(
        kafka_topic,
        group_id="group2",
        bootstrap_servers=eval(kafka_broker)
    )
    # consuming
    for msg in consumer:
        lines = bytes.decode(msg.value)
        line_json = json.loads(lines)
        if line_json.get("table_name") in eval(base_table):
            if line_json.get("client_ip") in checkip:
                continue
            if line_json.get("server_ip") in checkip:
                continue
            with open(find_tcp_path[0], 'a+') as d_file:
                d_file.write(lines)
                d_file.write('\n')
                #print(lines)
        if line_json.get("table_name") in eval(other_table):
            with open(find_other_path[0], 'a+') as o_file:
                o_file.write(lines)
                o_file.write('\n')
                #print(lines)

def main(ui_name):
    if ui_name in ["kafka"]:
        db_kafka_agent()

#main("kafka")

