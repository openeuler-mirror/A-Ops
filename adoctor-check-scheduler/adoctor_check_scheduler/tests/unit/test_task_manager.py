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
Date: 2021/9/1 23:35
docs: test_task_manager.py
description: test task manager
"""

import unittest
from unittest import mock
from adoctor_check_scheduler.check_scheduler.task_manager import check_task_manager


class TestTaskManager(unittest.TestCase):
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

    def tearDown(self) -> None:
        check_task_manager._retry_id_list.clear()
        check_task_manager._dead_retry_task.clear()
        while not check_task_manager._retry_queue.empty():
            check_task_manager._retry_queue.get()

    def test_create_retry_task(self):
        task = check_task_manager.create_retry_task(-1, [111, 222],
                                                    self.check_item_list, "admin", self.host_list)
        self.assertDictEqual({task.task_id: task}, check_task_manager._retry_id_list)
        check_task_manager.create_retry_task(task.task_id, [111, 222],
                                             self.check_item_list, "admin", self.host_list)
        self.assertDictEqual({task.task_id: task}, check_task_manager._retry_id_list)
        check_task_manager._retry_id_list.clear()
        check_task_manager._dead_retry_task.append(task.task_id)
        self.assertIsNone(check_task_manager.create_retry_task(task.task_id, [111, 222],
                                                               self.check_item_list, "admin",
                                                               self.host_list))

    def test_add_dead_retry_task(self):
        check_task_manager._add_dead_retry_task(111)
        self.assertListEqual(check_task_manager._dead_retry_task, [111])
        num = 1
        while num < check_task_manager.max_dead_retry_task_num:
            check_task_manager._add_dead_retry_task(num)
            self.assertEqual(len(check_task_manager._dead_retry_task), num + 1)
            num += 1
        self.assertEqual(len(check_task_manager._dead_retry_task),
                         check_task_manager.max_dead_retry_task_num)

    def test_enqueue_retry_task(self):
        task = check_task_manager.create_retry_task(-1, [111, 222],
                                                    self.check_item_list, "admin", self.host_list)
        check_task_manager.enqueue_retry_task(task)
        self.assertEqual(check_task_manager._retry_queue.qsize(), 1)
        self.assertEqual(task._enqueue_count, 1)
        task = check_task_manager._retry_queue.get()

        num = 1
        while num <= task.max_retry_num:
            task.try_again()
            num += 1
        check_task_manager.enqueue_retry_task(task)
        self.assertEqual(check_task_manager._retry_queue.qsize(), 0)
        self.assertGreater(task._enqueue_count, task.max_retry_num)

    def test_dequeue_retry_task(self):
        task1 = check_task_manager.create_retry_task(-1, [111, 222],
                                                     self.check_item_list, "admin", self.host_list)
        check_task_manager.enqueue_retry_task(task1)

        task2 = check_task_manager.create_retry_task(112, [111, 222],
                                                     self.check_item_list, "admin", self.host_list)

        check_task_manager.enqueue_retry_task(task2)
        task2._enqueue_time = 1111

        task = check_task_manager.dequeue_retry_task()
        self.assertEqual(task2.task_id, task.task_id)
        self.assertEqual(check_task_manager._retry_queue.qsize(), 1)
        self.assertIsNone(check_task_manager.dequeue_retry_task())

    def test_create_task_msg(self):
        host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                     {"host_id": "22222", "public_ip": "90.90.64.64"},
                     {"host_id": "33333", "public_ip": "90.90.64.66"}]

        ret = check_task_manager.create_task_msg([111, 222], [], "admin", host_list)
        msg = {
            "task_id": 0,
            "host_list": host_list,
            "user": "admin",
            "check_items": [],
            "time_range": [111, 222]
        }
        self.assertDictEqual(msg, ret)

    @mock.patch("adoctor_check_scheduler.check_scheduler.task_manager.MyResponse.get_response")
    def test_get_host_list(self, mock_get_response):
        expected_res = {
            'code': 200,
            'host_infos': {
                'admin': [{
                    'host_group_name': 'group1',
                    'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                    'host_name': '90.90.64.65',
                    'public_ip': '90.90.64.65',
                    'ssh_port': 22
                },
                    {
                        'host_group_name': 'group1',
                        'host_id': 'f485bd26070211ecaa06a01c8d75c8f3',
                        'host_name': '90.90.64.64',
                        'public_ip': '90.90.64.64',
                        'ssh_port': 22
                    },
                    {
                        'host_group_name': 'group1',
                        'host_id': 'fa05c1ba070211ecad52a01c8d75c8f3',
                        'host_name': '90.90.64.66',
                        'public_ip': '90.90.64.66',
                        'ssh_port': 22
                    }]
            },
            'msg': 'openrationsucceed'
        }
        mock_get_response.return_value = expected_res
        new_host_info = check_task_manager.get_host_list()
        ret = {"admin": [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                          'public_ip': '90.90.64.65'},
                         {'host_id': 'f485bd26070211ecaa06a01c8d75c8f3',
                          'public_ip': '90.90.64.64'},
                         {'host_id': 'fa05c1ba070211ecad52a01c8d75c8f3',
                          'public_ip': '90.90.64.66'}
                         ]}
        self.assertDictEqual(ret, new_host_info)
