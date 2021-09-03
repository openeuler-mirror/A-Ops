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
Date: 2021/9/2 14:25
docs: test_check_consumer.py
description: test check consumer
"""
import unittest
from adoctor_check_scheduler.common.constant import CheckTopic, CheckGroup
from adoctor_check_scheduler.common.config import scheduler_check_config
from adoctor_check_scheduler.common.check_consumer import RetryTaskConsumer, CheckConsumer
from adoctor_check_scheduler.check_scheduler.task_manager import check_task_manager


class TestCheckConsumer(unittest.TestCase):
    def test_stop_consumer(self):
        consumer = CheckConsumer("test_topic", "test_group", scheduler_check_config)
        consumer.stop_consumer()
        self.assertFalse(consumer._running_flag)


class TestRetryConsumer(unittest.TestCase):
    def test_process_msg(self, ):
        msg = {'task_id': 1630563905431, 'user': 'admin',
               'host_list': [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                              'public_ip': '90.90.64.65'}],
               'check_items': ['check_item2'],
               'time_range': [1630563874, 1630563904]}
        retry_consumer = RetryTaskConsumer(CheckTopic.retry_check_topic,
                                           CheckGroup.retry_check_group_id,
                                           scheduler_check_config)
        retry_consumer._process_msgs(msg)
        self.assertEqual(check_task_manager._retry_queue.qsize(), 1)
