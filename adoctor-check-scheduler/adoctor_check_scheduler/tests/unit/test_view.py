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
Date: 2021/8/25 11:11
docs: test_view.py
description: test view
"""

import unittest
from unittest import mock
from flask import Flask
import adoctor_check_scheduler.view
import adoctor_check_scheduler
from aops_utils.conf.constant import CHECK_IMPORT_RULE, CHECK_DELETE_RULE, \
    CHECK_GET_RULE, CHECK_COUNT_RULE, CHECK_GET_RESULT, CHECK_COUNT_RESULT
from aops_utils.kafka.producer import BaseProducer
from aops_utils.restful.response import MyResponse

header = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "81fe"
}


class TestCheckScheduler(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("manager")

        for blue, api in adoctor_check_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_import_check_rule(self):
        test_data = {'check_items': [
            {'check_item': 'check_item1', 'data_list': [{'name': 'data_item1',
                                                         'label': {'mode': 'irq'}}],
             'condition': '>1', 'plugin': '', 'description': 'aaa'},
            {'check_item': 'check_item2', 'data_list': [{'name': 'data_item2',
                                                         'label': {'mode': 'irq'}},
                                                        {'name': 'data_item3',
                                                         'label': {'mode': 'irq',
                                                                   'device': '125s0f0'}}],
             'condition': 'data_item2 + data_item3 < 10', 'plugin': '',
             'description': 'bbb'}
        ]}
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'openration succeed',
            }
            mock_get_response.return_value = expected_res
            with mock.patch.object(BaseProducer, "send_msg"):
                response = self.client.post(CHECK_IMPORT_RULE, json=test_data, headers=header)
                res = response.json
                self.assertDictEqual(res, expected_res)

    def test_get_check_rule(self):
        test_data = {
            "check_items": ["check_item1", "check_item7"],
            "page": 1,
            "per_page": 50
        }
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": "ok",
                "total_count": 1,
                "total_page": 1,
                "check_items": [
                    {
                        "check_item": "item1",
                        "data_list": ["data1", "data2"],
                        "check_condition": "zzz",
                        "check_result_description": "xxx",
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            response = self.client.post(CHECK_GET_RULE, json=test_data, headers=header)
            res = response.json
            self.assertDictEqual(res, expected_res)

    def test_delete_check_rule(self):
        test_data = {
            "check_items": ["check_item1", "check_item7"]
        }
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'openration succeed',
            }
            mock_get_response.return_value = expected_res
            with mock.patch.object(BaseProducer, "send_msg"):
                response = self.client.delete(CHECK_DELETE_RULE, json=test_data, headers=header)
                res = response.json
                self.assertDictEqual(res, expected_res)

    def test_count_check_rule(self):
        test_data = {}
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": "",
                "rule_count": 30
            }
            mock_get_response.return_value = expected_res
            response = self.client.post(CHECK_COUNT_RULE, json=test_data, headers=header)
            res = response.json
            self.assertDictEqual(res, expected_res)

    def test_count_check_result(self):
        test_data = {
            "host_list": [],
            "page": 1,
            "per_page": 50
        }
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": "openration succeed",
                "results": [
                    {
                        "count": 342,
                        "host_id": "fa05c1ba070211ecad52a01c8d75c8f3"
                    },
                    {
                        "count": 289,
                        "host_id": "eca3b022070211ecab3ca01c8d75c8f3"
                    },
                    {
                        "count": 268,
                        "host_id": "f485bd26070211ecaa06a01c8d75c8f3"
                    }
                ],
                "total_count": 3,
                "total_page": 1
            }
            mock_get_response.return_value = expected_res
            response = self.client.post(CHECK_COUNT_RESULT, json=test_data, headers=header)
            res = response.json
            self.assertDictEqual(res, expected_res)

    def test_get_check_result(self):
        test_data = {
            "time_range": [1630050000, 1630056585],
            "check_items": ["check_item1", "check_item7"],
            "host_list": [],
            "page": 1,
            "per_page": 50
        }
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "check_result": [
                    {
                        "check_item": "check_item6",
                        "condition": "keyword('error') == True",
                        "data_list": [
                            {
                                "data_name_str": "dmesg[]",
                                "macro": "$0",
                                "name": "dmesg",
                                "type": "log"
                            }
                        ],
                        "end": 1630548567,
                        "host_id": "f485bd26070211ecaa06a01c8d75c8f3",
                        "start": 1630548552,
                        "value": "Abnormal"
                    },
                    {
                        "check_item": "check_item6",
                        "condition": "keyword('error') == True",
                        "data_list": [
                            {
                                "data_name_str": "dmesg[]",
                                "macro": "$0",
                                "name": "dmesg",
                                "type": "log"
                            }
                        ],
                        "end": 1630548582,
                        "host_id": "fa05c1ba070211ecad52a01c8d75c8f3",
                        "start": 1630548552,
                        "value": "No data"
                    }
                ],
                "code": 200,
                "msg": "openration succeed",
                "total_count": 204,
                "total_page": 5
            }
            mock_get_response.return_value = expected_res
            response = self.client.post(CHECK_GET_RESULT, json=test_data, headers=header)
            res = response.json
            self.assertDictEqual(res, expected_res)
