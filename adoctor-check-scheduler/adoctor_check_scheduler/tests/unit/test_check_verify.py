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
Date: 2021/8/23 17:19
docs: test_check_verify.py.py
description:
"""

import unittest
from adoctor_check_scheduler.common.check_verify import ImportRuleSchema, GetCheckResultSchema, \
    DeleteCheckRuleSchema, GetCheckResultCountSchema
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import SUCCEED, PARAM_ERROR

test_data = {'check_items': [
    {'check_item': 'check_item1', 'data_list': [{'name': 'data_item1', 'type': 'kpi',
                                                 'label': {'mode': 'irq'}}],
     'condition': '>1', 'plugin': '', 'description': 'aaa'},
    {'check_item': 'check_item2', 'data_list': [{'name': 'data_item2', 'type': 'kpi',
                                                 'label': {'mode': 'irq'}},
                                                {'name': 'data_item3', 'type': 'kpi',
                                                 'label': {'mode': 'irq', 'device': '125s0f0'}}],
     'condition': 'data_item2 + data_item3 < 10', 'plugin': '', 'description': 'bbb'},
    {'check_item': 'check_item3',
     'data_list': [{'name': 'data_item2', 'type': 'kpi', 'label': {'mode': 'idle'}},
                   {'name': 'data_item4', 'type': 'log'}],
     'condition': 'func1(data_item2, data_item4) < 5', 'plugin': '',
     'description': 'ccc'},
    {'check_item': 'check_item4', 'data_list': [{'name': 'data_item5', 'type': 'log'}],
     'condition': 'max(data_item5) < 10',
     'plugin': '', 'description': ''},
    {'check_item': 'check_item5', 'data_list': [{'name': 'data_item6', 'type': 'kpi' }],
     'condition': 'func2(data_item6, 100, "reboot") == True', 'plugin': '',
     'description': 'ddd'}]}


class TestCheckVerify(unittest.TestCase):
    def test_import_check_rule_schema(self):
        verify_res = MyResponse.verify_all(
            test_data, ImportRuleSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)

    def test_get_check_result_schema(self):
        test_msg = {
            "time_range": [1630050000, 1630056585],
            "check_items": ["check_item1", "check_item7"],
            "host_list": [],
            "page": 1,
            "per_page": 50,
            "sort": "check_item",
            "direction": "asc"
        }
        verify_res = MyResponse.verify_all(test_msg, GetCheckResultSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)
        test_msg = {
            "time_range": [],
            "check_items": [],
            "host_list": [],
            "page": 1,
            "per_page": 10,
            "sort": "check_item",
            "direction": "asc"
        }
        verify_res = MyResponse.verify_all(test_msg, GetCheckResultSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)

        test_msg = {
            "time_range": [111],
            "check_items": [],
            "host_list": [],
            "page": 1,
            "per_page": 10,
            "sort": "check_item",
            "direction": "asc"
        }
        verify_res = MyResponse.verify_all(test_msg, GetCheckResultSchema, "1234")
        self.assertEqual(verify_res, PARAM_ERROR)

    def test_delete_check_rule_schema(self):
        test_msg = {
            "check_items": ["cpu_usage_overflow"]
        }
        verify_res = MyResponse.verify_all(
            test_msg, DeleteCheckRuleSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)

        test_msg = {
            "check_items": []
        }
        verify_res = MyResponse.verify_all(
            test_msg, DeleteCheckRuleSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)

    def test_get_check_result_count_schema(self):
        test_msg = {
            "host_list": [],
            "page": 1,
            "per_page": 50,
            "sort": "count",
            "direction": "desc"
        }
        verify_res = MyResponse.verify_all(
            test_msg, GetCheckResultCountSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)

        test_msg = {
            "host_list": ["qqqq"],
            "page": 1,
            "per_page": 50,
            "sort": "",
            "direction": "asc"
        }
        verify_res = MyResponse.verify_all(
            test_msg, GetCheckResultCountSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)


if __name__ == '__main__':
    unittest.main()
