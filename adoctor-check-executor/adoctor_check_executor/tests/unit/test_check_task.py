#!/usr/bin/python3
# -*- coding:UTF=8 -*-
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
Date: 2021/9/1 17:40
docs: test_check_task.py
description: test check task
"""

import unittest
from unittest import mock
from adoctor_check_executor.check_executor.check_task import CheckTask
from adoctor_check_executor.check_executor.check_item import CheckItem, CheckItemDetail


class TestCheckTask(unittest.TestCase):
    def test_build_host_list_map(self):
        host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                     {"host_id": "22222", "public_ip": "90.90.64.64"},
                     {"host_id": "33333", "public_ip": "90.90.64.66"}]
        host_list_map = CheckTask.build_host_list_map(host_list)
        ret = {"11111": {"host_id": "11111", "public_ip": "90.90.64.65"},
               "22222": {"host_id": "22222", "public_ip": "90.90.64.64"},
               "33333": {"host_id": "33333", "public_ip": "90.90.64.66"}}
        self.assertDictEqual(host_list_map, ret)

    def create_task_msg(self):
        host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                     {"host_id": "22222", "public_ip": "90.90.64.64"},
                     {"host_id": "33333", "public_ip": "90.90.64.66"}]

        ret = CheckTask.create_task_msg([111, 222], [], "admin", host_list)
        msg = {
            "task_id": 0,
            "host_list": host_list,
            "user": "admin",
            "check_items": [],
            "time_range": [111, 222]
        }
        self.assertDictEqual(msg, ret)

    @mock.patch("adoctor_check_executor.check_executor.check_task.check_item_manager")
    def test_import_check_items(self, mock_check_item_manager):
        check_item_config = {
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            }],
            "condition": "data_item1>1",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        }
        check_item_detail = CheckItemDetail("admin", check_item_config)
        check_item = CheckItem(check_item_detail)
        mock_check_item_manager.get_check_item_list.return_value = [check_item]
        mock_check_item_manager.get_check_item.return_value = check_item
        check_task = CheckTask()
        check_task.import_check_items("admin", [])
        self.assertListEqual(check_task.check_item_list, [check_item])
        check_task.check_item_list.clear()
        check_task.import_check_items("admin", ["check_item1"])
        self.assertListEqual(check_task.check_item_list, [check_item])
        check_task.check_item_list.clear()
