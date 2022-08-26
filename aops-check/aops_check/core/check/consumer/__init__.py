#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
import threading
from kafka.errors import KafkaError

from aops_utils.kafka.consumer import BaseConsumer
from aops_utils.kafka.kafka_exception import ConsumerInitError
from aops_utils.log.log import LOGGER

from aops_check.utils.register import Register


class Consumer(threading.Thread):
    """
    Consumer of kafka
    """
    __slots__ = ['__consumer', '__topic', '__group_id', '__running_flag']

    def __init__(self, topic: str, group_id: str, configuration):
        """
        Init consumer
        """
        threading.Thread.__init__(self)
        try:
            self.__consumer = BaseConsumer(topic, group_id, configuration)
        except ConsumerInitError as exp:
            LOGGER.error("Get consumer failed, %s", exp)
        self.__topic = topic
        self.__group_id = group_id
        self.__running_flag = True

    @property
    def consumer(self):
        return self.__consumer

    @property
    def topic(self):
        return self.__topic

    @property
    def group_id(self):
        return self.__group_id

    @property
    def running_flag(self):
        return self.__running_flag

    @running_flag.setter
    def running_flag(self, value):
        self.__running_flag = value

    def stop_consumer(self):
        """
        stop consumer thread
        """
        LOGGER.info("Stop consumer topic:%s group:%s",
                    self.topic, self.group_id)
        self.running_flag = False

    def run(self):
        """
        manually pull messages from broker, the number of messages is based on max_records.
        """
        LOGGER.info("start run topic: %s group: %s _consumer",
                    self.topic, self.group_id)
        try:
            while self.running_flag:
                data = self.consumer.poll()
                if not data:
                    continue
                self._parse_data(data)
        except KafkaError as err:
            LOGGER.error(err)

    def _parse_data(self, data):
        """
        Parse data of consumer
        Args:
            data (dict):
        """
        for key, value in data.items():
            for consumer_record in value:
                if not all([consumer_record, consumer_record.value]):
                    LOGGER.error("%s consumer_record is None.", key)
                    continue
                # Message Processing
                self._process_msgs(consumer_record.value)
                self.consumer.commit()

    def _process_msgs(self, msg):
        """
        Process msg (Inherit the implementation)
        """


class ConsumerManager:
    def __init__(self, consumer_list: list):
        self.consumer_list = consumer_list

    def __del__(self):
        self.stop()

    def run(self):
        for consumer in self.consumer_list:
            consumer.run()

    def stop(self):
        for consumer in self.consumer_list:
            consumer.stop_consumer()
