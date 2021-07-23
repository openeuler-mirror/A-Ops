from kafka import KafkaConsumer
import json
import re
import configparser

def main():
    # can specify a type of IP that isn't recorded
    checkip = r"0.0.0"
    # analysis configuration
    cf = configparser.ConfigParser()
    cf.read("gala-spider.conf", encoding="utf-8")
    db_agent = cf.get("global", "data_source")
    kafka_topic = cf.get(eval(db_agent), "topic")
    kafka_broker = cf.get(eval(db_agent), "broker")
    base_table = cf.get("table_info", "base_table_name")
    other_table = cf.get("table_info", "other_table_name")
    exclude_ip = cf.get("option", "exclude_addr")
    checkip = eval(exclude_ip)

    if eval(db_agent) == "kafka":
        # kafka consumer conf
        consumer = KafkaConsumer(
            kafka_topic,
            group_id="group2",
            bootstrap_servers=eval(kafka_broker)
        )

    for msg in consumer:
        lines = bytes.decode(msg.value)
        line_json = json.loads(lines)
        if line_json.get("table_name") in eval(base_table):
            with open("tcpline.txt", 'a+') as d_file:
                if re.match(checkip, line_json.get("client_ip")) is not None:
                    continue
                if re.match(checkip, line_json.get("server_ip")) is not None:
                    continue
                d_file.write(lines)
                d_file.write('\n')
                #print(lines)
        if line_json.get("table_name") in eval(other_table):
            with open("otherline.txt", 'a+') as o_file:
                o_file.write(lines)
                o_file.write('\n')
                #print(lines)


if __name__ == '__main__':
    main()

