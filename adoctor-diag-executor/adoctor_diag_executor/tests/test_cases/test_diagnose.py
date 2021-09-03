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
import os
import json
import unittest
from adoctor_diag_executor.function.diagnose import parse_check_result, diagnose

__here__ = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(__here__, "../data/")


class TestDiagnose(unittest.TestCase):

    def test_diagnose(self):
        tree_example = os.path.join(data_path, "tree_example.json")
        with open(tree_example, 'r', encoding="UTF-8") as json_file:
            tree_json = json_file.read()
        tree_content = json.loads(tree_json)
        args = {
                "username": "admin",
                "host_id": "host1",
                "tree_name": "tree2",
                "tree_content": tree_content,
                "time_range": [112221122, 112221222],
                "task_id": "5eaaea18061411ec8761a01c8d75c92f"
            }
        res = diagnose(args)

        expected_res_json = os.path.join(data_path, "report1.json")
        with open(expected_res_json, 'r', encoding="UTF-8") as json_file:
            expected_report_json = json_file.read()
            expected_report_dict = json.loads(expected_report_json)

        res.pop("report_id")
        expected_report_dict.pop("report_id")

        self.assertDictEqual(res, expected_report_dict)

    def test_parse_check_result(self):
        args = {
            "code": 200,
            "msg": "",
            "total_count": 1,
            "total_page": 1,
            "check_result": [
                {"host_id": "host1", "data_list": ["data1", "data2"], "start": 11, "end": "25",
                 "check_item": "check_item1", "condition": "", "value": "Abnormal"},
                {"host_id": "host1", "data_list": ["data2", "data3"], "start": 11, "end": "25",
                 "check_item": "check_item2", "condition": "", "value": "No data"},
                {"host_id": "host1", "data_list": ["data2", "data3"], "start": 11, "end": "25",
                 "check_item": "check_item3", "condition": "", "value": "aaa"}
            ]
        }

        parse_res = parse_check_result({"check_item1", "check_item2", "check_item3"}, args)
        self.assertEqual(parse_res, {'abnormal': {'check_item1'}, 'no data': {'check_item2'},
                                     'internal error': {'check_item3'}})

        args["code"] = 500
        parse_res = parse_check_result({"check_item1", "check_item2", "check_item3"}, args)
        self.assertEqual(parse_res, {'abnormal': set(), 'no data': set(),
                                     'internal error': {'check_item1', 'check_item2', 'check_item3'}})
