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
from typing import Any, Dict

from kafka import KafkaConsumer as Consumer
from kafka import KafkaProducer as Producer

from anteater.utils.log import Log

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
    def __init__(self, server: str, port: str) -> None:
        conf = {"bootstrap_servers": f"{server}:{port}"}
        self.producer = Producer(**conf)

    def send_message(self, topic: str, messages: Dict[str, Any]):
        """
        Sent the message to Kafka
        :param topic: The kafka topic
        :param messages: The messages
        :return: None
        """
        self.producer.send(topic, json.dumps(messages).encode('utf-8'))
        self.producer.flush()


class KafkaConsumer(threading.Thread):
    """
    The Kafka Consumer to consume messages from Kafka.
    """
    def __init__(self, server, port, topic):
        """
        The Kafka Consumer initializer
        :param server: The kafka server ip
        :param port: The kafka server port
        :param topic: The topic
        """
        threading.Thread.__init__(self)
        self.topic = topic
        conf = {"bootstrap_servers": f"{server}:{port}",
                "group_id": f"anomaly_detection_{uuid.uuid4()}",
                "auto_offset_reset": "earliest",
                "enable_auto_commit": False}
        self.consumer = Consumer(self.topic, **conf)

    @staticmethod
    def message_process(metadata):
        """Processes the kafka messages and update the shared variables"""
        if metadata.get("meta_name", "") == "ksliprobe":
            EntityVariable.variable = metadata

    def run(self):
        """Run Kafka Consumer to collect messages"""
        for msg in self.consumer:
            data = json.loads(msg.value)
            metadata = {}
            metadata.update(data)

            self.message_process(metadata)
