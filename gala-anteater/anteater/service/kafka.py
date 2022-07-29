#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: The implementation of Kafka Consumer and Producer.
"""

import json
import threading
import uuid

from confluent_kafka import Producer, Consumer

from utils.log import Log

log = Log().get_logger()


class EntityVariable:
    """
    The global variables which will be used to update
    some key settings through multiprocessors
    """
    variable = None


class KafkaProducer:
    """
    The Kafka Producer to sent message to kafka.
    """
    def __init__(self, server: str, port: str):
        self.server = server
        self.port = port

        self.producer = Producer({"bootstrap.servers": f"{server}:{port}"})

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            log.error(f"Message delivery failed.{err}, msg: {msg}")

    def send_message(self, topic, messages):
        """
        Sent the message to Kafka
        :param topic: The kafka topic
        :param messages: The messages
        :return: None
        """
        self.producer.poll(0)
        self.producer.produce(topic, json.dumps(messages).encode('utf-8'), callback=self.delivery_report)
        self.producer.flush()


class KafkaConsumer(threading.Thread):
    """
    The Kafka Consumer to consume messages from Kafka.
    """
    def __init__(self, server, port, topics):
        """
        The Kafka Consumer initializer
        :param server: The kafka server ip
        :param port: The kafka server port
        :param topics: The topics
        """
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.topics = [topics] if isinstance(topics, str) else topics
        self.begin = False

        conf = {'bootstrap.servers': f"{server}:{port}",
                'group.id': f"anomaly_detection_testing_{uuid.uuid4()}",
                'auto.offset.reset': 'earliest',
                "enable.auto.commit": False}

        self.consumer = Consumer(conf)

    @staticmethod
    def message_process(value):
        """Processes the kafka messages and update the shared variables"""
        result = json.loads(value.decode('utf8'))

        if result.get("meta_name", "") == "redis_client":
            EntityVariable.variable = result
            log.info("Loaded the latest CONF information!")

    def run(self):
        """Run Kafka Consumer to collect messages"""
        self.consume_loop()

    def consume_loop(self):
        """The consumer loop to fetch messages continuously"""
        try:
            self.consumer.subscribe(self.topics)

            while True:
                message = self.consumer.poll(timeout=5.0)
                if message is None:
                    continue

                if message.error():
                    log.error(f"{message.topic}, {message.partition()}, {message.offset()} reached end at offset")
                else:
                    self.message_process(message.value())
        finally:
            self.consumer.close()
