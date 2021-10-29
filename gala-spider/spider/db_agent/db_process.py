from kafka import KafkaConsumer
import ast
import json
from spider.util.conf import kafka_topic
from spider.util.conf import kafka_broker
from spider.util.conf import base_table
from spider.util.conf import other_table
from spider.util.conf import exclude_ip
from spider.util.conf import temp_tcp_file
from spider.util.conf import temp_other_file

def db_kafka_agent():
    print("------------- kafka process --------------")
    # kafka consumer conf
    consumer = KafkaConsumer(
        kafka_topic,
        group_id="group2",
        bootstrap_servers=ast.literal_eval(kafka_broker)
    )
    # can specify a type of IP that isn't recorded
    checkip = ast.literal_eval(exclude_ip)
    # consuming
    for msg in consumer:
        lines = bytes.decode(msg.value)
        line_json = json.loads(lines)
        if line_json.get("process_name") in ["sshd", "rdk:broker0"]:
            continue
        if line_json.get("table_name") in ast.literal_eval(base_table):
            if line_json.get("client_ip") in checkip:
                continue
            if line_json.get("server_ip") in checkip:
                continue
            with open(temp_tcp_file, 'a+') as d_file:
                d_file.write(lines)
                d_file.write('\n')
                #print(lines)
        if line_json.get("table_name") in ast.literal_eval(other_table):
            with open(temp_other_file, 'a+') as o_file:
                o_file.write(lines)
                o_file.write('\n')
                #print(lines)

def db_process_agent(ui_name):
    if ui_name in ["kafka"]:
        db_kafka_agent()

#db_process_agent("kafka")

