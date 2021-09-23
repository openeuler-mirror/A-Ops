#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
consumer class for consuming diagnose messages
"""
from kafka.errors import KafkaError

from aops_utils.log.log import LOGGER
from aops_utils.kafka.consumer import BaseConsumer
from adoctor_diag_executor.function.diagnose import diagnose, save_diag_result


class Consumer(BaseConsumer):
    """
    Consumer of kafka
    """
    def __init__(self, topic, group_id, configuration):
        """
        Init consumer object
        Args:
            topic (str): Consumer's topic
            group_id (str): Consumer group's id
            configuration (aops_utils.conf.Config object): config object of consumer's config file

        Raises: ConsumerInitError
        """
        super().__init__(topic, group_id, configuration)
        self._running_flag = True

    def consume_msg(self):
        """
        manually pull messages from broker, the number of messages is based on max_records.
        """
        try:
            while self._running_flag:
                data = self.poll()
                if data:
                    self.process_msgs(data)
        except KafkaError as err:
            LOGGER.error(err)

    def stop_consumer(self):
        """
        stop consumer
        """
        LOGGER.info("Stop consumer topic:%s group:%s", self.topic, self.conf["group_id"])
        self._running_flag = False

    def process_msgs(self, data):
        """
        Process messages, do diagnose logic
        Args:
            data (dict): messages from broker, key is an object of TopicPartition,
            value is a list of ConsumerRecord, and the value attribute is a dict of the message.
            e.g. ConsumerRecord: ConsumerRecord(topic="", partition=0,offset=11757,
                                timestamp=12345, timestamp_type=0,key=None, value="{}")
                value of ConsumerRecord:
                    {
                        "username": "admin",
                        "host_id": "host1",
                        "tree_name": "tree2",
                        "time_range": [112221122, 112221222],
                        "task_id": "5eaaea18-0614-11ec-8761-a01c8d75c92f"
                    }

        Returns:

        """
        reports = []

        for key, value in data.items():
            for consumer_record in value:
                if consumer_record is not None:
                    message_value = consumer_record.value
                    LOGGER.debug("Get job from kafka. %s" % message_value)
                    report = diagnose(message_value)
                    reports.append(report)
                    self.commit()
                else:
                    LOGGER.error("%s consumer_record is None." % key)

        save_diag_result({"reports": reports})
