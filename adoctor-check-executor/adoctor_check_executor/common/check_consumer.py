#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/4 17:20
docs: check_consumer.py
description: msg transporter
"""
import threading
from adoctor_check_executor.check_executor.check_item_manager import check_item_manager
from adoctor_check_executor.check_executor.check_task import CheckTask
from adoctor_check_executor.common.check_error import CheckExceptionList
from adoctor_check_executor.common.check_verify import CheckTaskMsgSchema
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import SUCCEED
from aops_utils.kafka.consumer import BaseConsumer
from aops_utils.kafka.kafka_exception import ConsumerInitError
from aops_utils.log.log import LOGGER



class CheckConsumer(threading.Thread):
    """
    Consumer of kafka
    """

    def __init__(self, topic, group_id, configuration):
        """
        Init consumer
        """
        threading.Thread.__init__(self)
        try:
            self._consumer = BaseConsumer(topic, group_id, configuration)
        except ConsumerInitError as exp:
            LOGGER.error("Get consumer failed, ", exp)
        self._topic = topic
        self._group_id = group_id
        self._running_flag = True

    def stop_consumer(self):
        """
        stop consumer thread
        """
        LOGGER.info("Stop consumer topic:%s group:%s", self._topic, self._group_id)
        self._running_flag = False

    def run(self):
        """
        manually pull messages from broker, the number of messages is based on max_records.
        """
        LOGGER.info("start run topic: %s group: %s _consumer", self._topic, self._group_id)
        try:
            while self._running_flag:
                data = self._consumer.poll()
                if not data:
                    continue
                self._parse_data(data)
        except CheckExceptionList as err:
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
                try:
                    self._process_msgs(consumer_record.value)
                except CheckExceptionList as exp:
                    LOGGER.error("consumer msg exp ", exp)
                self._consumer.commit()

    def _process_msgs(self, msg):
        """
        Process msg （Inherit the implementation）
        """


class ImportRuleConsumer(CheckConsumer):
    """
    The consumer to get import check rule msg
    """

    def _process_msgs(self, msg):
        """
        Process messages, do import rule logic
        Args:
            msg (dict): messages from broker, key is an object of TopicPartition,
                         value is a list of ConsumerRecord

        Returns:

        """
        user = msg.get("username")
        if not user:
            LOGGER.error("Unknown user of the check item")
            return
        check_item_list = msg.get("check_items", {})
        check_item_manager.import_check_item(user, check_item_list)


class DelRuleConsumer(CheckConsumer):
    """
    The consumer to get delete check rule msg
    """

    def _process_msgs(self, msg):
        """
        Process messages, do diagnose logic
        Args:
            msg (dict): messages from broker, key is an object of TopicPartition,
                         value is a list of ConsumerRecord

        Returns:

        """
        LOGGER.debug("msg: %s", msg)
        user = msg.get("username")
        if not user:
            LOGGER.error("Unknown user of the check item")
            return
        check_item_list = msg.get("check_items", {})
        check_item_manager.delete_check_item(user, check_item_list)


class DoCheckConsumer(CheckConsumer):
    """
    The consumer to get do check msg
    """

    def _process_msgs(self, msg):
        """
        Process messages, do diagnose logic
        Args:
            msg (dict): messages from broker, key is an object of TopicPartition,
                         value is a list of ConsumerRecord

        Returns:

        """
        LOGGER.debug("msg: %s", msg)
        verify_res = MyResponse.verify_args(
            msg, CheckTaskMsgSchema)
        if verify_res != SUCCEED:
            LOGGER.error("Invalid msg from retry producer")
            return

        time_range = msg.get("time_range")
        host_list = msg.get("host_list")
        user = msg.get("user")
        task_id = msg.get("task_id")
        check_items = msg.get("check_items", [])

        check_task = CheckTask()
        check_task.import_check_items(user, check_items)
        check_task.do_check(time_range, user, host_list, task_id)
