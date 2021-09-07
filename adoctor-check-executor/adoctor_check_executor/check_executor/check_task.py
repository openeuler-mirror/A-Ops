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
Author: YangYunYi
Date: 2021/8/7 21:36
docs: check_task.py
description: Check task
"""
from adoctor_check_executor.check_executor.check_item_manager import check_item_manager
from adoctor_check_executor.common.constant import CheckTopic, CheckResultType, BACKWARD_TASK_ID
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.common.check_msg import CheckMsgToolKit
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER


class CheckTask:
    """
    The manager of Check rule

    Attributes:
        check_item_list (list): check item list
    """

    def __init__(self):
        """
        Constructor
        """
        self.check_item_list = []

    def import_check_items(self, user, check_items):
        """
        Import check items from check item manager
        Args:
            user (str) : user of check task
            check_items (list): check item name list

        Returns:
            None
        """
        if not check_items:
            self.check_item_list = check_item_manager.get_check_item_list(user)
            LOGGER.debug("check_items is [], get all check items of user %s", user)
            return

        for check_item_name in check_items:
            check_item = check_item_manager.get_check_item(user, check_item_name)
            if check_item:
                self.check_item_list.append(check_item)

    def do_check(self, time_range, user, host_list, task_id):
        """
        Import check items from check item manager
        Args:
            time_range (list): time range [start_ts, end_ts]
            user (str): the user of check task
            host_list (list): host list
            task_id (int): task id

        Returns:
            None
        """
        LOGGER.debug("========start check task: time_range %s, "
                     "task_id %s===========",
                     time_range, task_id)
        abnormal_data_result = []
        # If no rule has been imported, the retry task for the time segment is returned.
        if not self.check_item_list:
            try:
                producer = BaseProducer(executor_check_config)
                abnormal_msg = CheckTask.create_task_msg(time_range,
                                                         [],
                                                         user,
                                                         host_list,
                                                         task_id)

                producer.send_msg(CheckTopic.retry_check_topic, abnormal_msg)
            except ProducerInitError as exp:
                LOGGER.error("get producer failed", exp)
            LOGGER.error("Cannot get check items")
            return

        # Do check for all check items
        for check_item in self.check_item_list:
            abnormal_data_list = check_item.do_check(time_range, host_list)
            abnormal_data_result.extend(abnormal_data_list)

        # Save check result to database
        if len(abnormal_data_result) > 0:
            CheckMsgToolKit.save_check_result_to_database(abnormal_data_result)

        # backward task no need retry
        if task_id == BACKWARD_TASK_ID:
            return

        # Send retry msg to scheduler
        try:
            producer = BaseProducer(executor_check_config)
            #
            host_list_map = self.build_host_list_map(host_list)
            for abnormal_data in abnormal_data_result:
                if abnormal_data.get("value") == CheckResultType.abnormal:
                    continue
                abnormal_msg = CheckTask.create_task_msg([abnormal_data.get("start"),
                                                          abnormal_data.get("end")],
                                                         [abnormal_data.get("check_item")],
                                                         abnormal_data.get("username"),
                                                         [host_list_map.get(
                                                             abnormal_data.get("host_id"))],
                                                         task_id)

                producer.send_msg(CheckTopic.retry_check_topic, abnormal_msg)
        except ProducerInitError as exp:
            LOGGER.error("Produce abnormal msg failed, %s" % exp)

    @staticmethod
    def build_host_list_map(host_list):
        """
        Create the mapping between host_id and host_info.
        Args:
            host_list (list): host info list
                            [{"host_id":"xxxx", "public_ip":"x.x.x.x"},
                            {"host_id":"yyyy", "public_ip":"y.y.y.y"}]

        Returns:
            host_info_map (dict):
            {"xxxx":{"host_id":"xxxx", "public_ip":"x.x.x.x"},
            "yyyy":{"host_id":"yyyy", "public_ip":"y.y.y.y"}}
        """
        host_list_map = dict()
        for host in host_list:
            host_list_map[host.get("host_id")] = host
        return host_list_map

    @staticmethod
    def create_task_msg(time_range, check_item_list, user, host_list, task_id=0):
        """
        Create retry task msg
        Args:
            time_range (list): time range [start_ts, end_ts]
            user (str): the user of the check task
            host_list (list): host list
            task_id (int): task id
            check_item_list (list): check item list

        Returns:
            msg (Dict)
        """
        msg = {"task_id": task_id,
               "user": user,
               "host_list": host_list,
               "check_items": check_item_list,
               "time_range": time_range}
        return msg
