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
Date: 2021/8/25 17:32
docs: test_check_item.py
description: test check item
"""

import unittest
from unittest import mock
from adoctor_check_executor.check_executor.check_item import CheckItemDetail, CheckItem
from adoctor_check_executor.common.check_error import CheckItemError


class TestCheckItemDetail(unittest.TestCase):
    def test_build_check_item_detail(self):
        check_item_config = {
            "check_item": "",
            "data_list": [],
            "condition": "",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        }
        with self.assertRaises(CheckItemError):
            CheckItemDetail("admin", check_item_config)

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
        self.assertEqual(check_item_detail.check_item_name, "check_item1")
        self.assertListEqual(check_item_detail.data_list, [{
            "name": "data_item1",
            "label": {
                "mode": "irq"
            }
        }])
        self.assertEqual(check_item_detail.check_condition, "data_item1>1")
        self.assertEqual(check_item_detail.check_rule_plugin_name, "expression_rule_plugin")
        self.assertEqual(check_item_detail.check_result_description, "aaa")
        self.assertEqual(check_item_detail.user, "admin")

    def test_get_check_item_detail(self):
        check_item_config = {
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            },
                {
                    "name": "data_item2",
                    "label": {
                        "cpu": "1"
                    }
                }
            ],
            "condition": "data_item1>1",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        }
        check_item_detail = CheckItemDetail("admin", check_item_config)
        abnormal_data = {'data_list': [{'name': 'data_item1', 'label': {'mode': 'irq'}},
                                       {'name': 'data_item2', 'label': {'cpu': '1'}}],
                         'check_item': 'check_item1',
                         'condition': 'data_item1>1',
                         'plugin': 'expression_rule_plugin',
                         'description': 'aaa',
                         'username': 'admin'}
        self.assertDictEqual(check_item_detail.get_check_item_detail(), abnormal_data)


class TestCheckItem(unittest.TestCase):
    def test_add_abnormal_data(self):
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
        abnormal_data_list = []
        CheckItem.add_abnormal_data(check_item_detail, [1111, 2222], "11111",
                                    "Internal error", abnormal_data_list)
        ret = [{'data_list': [{'name': 'data_item1', 'label': {'mode': 'irq'}}],
                'check_item': 'check_item1',
                'condition': 'data_item1>1',
                'plugin': 'expression_rule_plugin',
                'description': 'aaa',
                'username': 'admin', 'host_id': '11111',
                'start': 1111, 'end': 2222,
                'value': 'Internal error'}]
        self.assertListEqual(abnormal_data_list, ret)

    @mock.patch("adoctor_check_executor.check_executor.check_item.DataManager")
    def test_prepare_data(self, mock_data_manager):
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
        host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                     {"host_id": "22222", "public_ip": "90.90.64.64"},
                     {"host_id": "33333", "public_ip": "90.90.64.66"}]
        check_item_detail = CheckItemDetail("admin", check_item_config)
        check_item = CheckItem(check_item_detail)
        mock_data_manager.query_data.return_value = None
        abnormal_data_list = []
        check_item.prepare_data([111, 222], host_list, abnormal_data_list)
        self.assertListEqual(check_item.host_list, host_list)


if __name__ == "__main__":
    unittest.main()
