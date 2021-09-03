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
Date: 2021/9/1 23:24
docs: test_retry_task.py
description: test retry task
"""

import unittest
from adoctor_check_scheduler.check_scheduler.retry_task import RetryTask


class TestRetryTask(unittest.TestCase):
    def setUp(self) -> None:
        self.check_item_list = [{
            "check_item": "check_item1",
            "data_list": [{
                "name": "node_cpu_seconds_total",
                "type": "kpi",
                "label": {
                    "cpu": "1",
                    "mode": "irq"
                }
            }],
            "condition": "$0>1",
            "plugin": "",
            "description": "aaa"
        }]

        self.host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                          {"host_id": "22222", "public_ip": "90.90.64.64"},
                          {"host_id": "33333", "public_ip": "90.90.64.66"}]

    def test_is_waiting(self):
        task = RetryTask(11111, [111, 222], self.check_item_list, "admin", self.host_list)
        self.assertFalse(task.is_waiting())
        task.try_again()
        self.assertTrue(task.is_waiting())

    def test_is_use_up(self):
        task = RetryTask(11111, [111, 222], self.check_item_list, "admin", self.host_list)
        retry_count = RetryTask.max_retry_num
        while retry_count > 0:
            self.assertFalse(task.is_use_up())
            task.try_again()
            retry_count -= 1
        task.try_again()
        self.assertTrue(task.is_use_up())

    def test_try_again(self):
        task = RetryTask(11111, [111, 222], self.check_item_list, "admin", self.host_list)
        task.try_again()
        self.assertNotEqual(task._enqueue_time, -1)
        self.assertEqual(task._enqueue_count, 1)
