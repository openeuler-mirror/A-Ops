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
Time:
Author:
Description:
"""
import time
import unittest

from aops_database.proxy.check import CheckDatabase
from aops_database.conf.constant import CHECK_RULE_INDEX, CHECK_RESULT_INDEX
from aops_database.factory.mapping import MAPPINGS
from aops_utils.restful.status import SUCCEED
from aops_utils.compare import compare_two_object


class TestCheckDatabase(unittest.TestCase):
    def setUp(self):
        # create engine to database
        host = "127.0.0.1"
        port = 9200
        self.proxy = CheckDatabase(host, port)
        self.proxy.connect()
        self.proxy.delete_index(CHECK_RULE_INDEX)
        self.proxy.delete_index(CHECK_RESULT_INDEX)
        self.proxy.create_index(CHECK_RULE_INDEX, MAPPINGS[CHECK_RULE_INDEX])
        self.proxy.create_index(
            CHECK_RESULT_INDEX, MAPPINGS[CHECK_RESULT_INDEX])

    def tearDown(self):
        self.proxy.delete_index(CHECK_RULE_INDEX)
        self.proxy.delete_index(CHECK_RESULT_INDEX)
        self.proxy.close()

    def test_api_check_rule(self):
        # ==============add check rule===================
        data = {
            "username": "test",
            "check_items": [
                {
                    "check_item": "memory_usage",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}, {"name":"a", "type":"kpi","label":{"mode":"haha"}}],
                    "condition": "c1",
                    "description": "bb"
                },
                {
                    "check_item": "cpu_usage",
                    "data_list": [{"name": "b", "type":"log", "label": {}}],
                    "condition": "c1",
                    "description": "xxx",
                    "plugin": "x"
                },
                {
                    "check_item": "disk_usage",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"cpu":"cpu1", "mode":"irq"}}],
                    "condition": "c1",
                    "description": "xxx",
                    "plugin": "aa"
                },
                {
                    "check_item": "io_usage",
                    "data_list": [],
                    "condition": "c1",
                    "description": "xxx"
                }
            ]
        }
        res = self.proxy.add_check_rule(data)
        self.assertEqual(len(res[1]["succeed_list"]), 4)
        time.sleep(1)

        data = {
            "username": "test",
            "check_items": [
                {
                    "check_item": "cpu_usage",
                    "data_list": [{"name": "b", "type":"log", "label": {}}],
                    "condition": "c5",
                    "description": "xxx",
                    "plugin": "aa"
                }
            ]
        }
        res = self.proxy.add_check_rule(data)
        self.assertEqual(len(res[1]["update_list"]), 1)
        time.sleep(1)
        # ==============get check rule===================
        data = {
            "username": "test",
            "check_items": [],
            "sort": "check_item",
            "direction": "desc",
            "page": 2,
            "per_page": 3
        }
        expected_res = {
            "total_count": 4,
            "check_items": [
                {
                    "check_item": "cpu_usage",
                    "data_list": [{"name": "b", "type":"log", "label": {}}],
                    "condition": "c5",
                    "description": "xxx",
                    "plugin": "aa"
                }
            ],
            "total_page": 2
        }
        res = self.proxy.get_check_rule(data)
        self.assertEqual(expected_res, res[1])

        data = {
            "username": "test",
            "check_items": [],
            "sort": "check_item",
            "direction": "desc",
        }
        res = self.proxy.get_check_rule(data)
        self.assertEqual(4, len(res[1]['check_items']))

        # =============delete rule =================
        data = {
            "username": "test",
            "check_items": ["disk_usage", "xxx"]
        }
        res = self.proxy.delete_check_rule(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        # =============get rule count=================
        data = {
            "username": "test"
        }
        res = self.proxy.get_rule_count(data)
        self.assertEqual(res[1]["rule_count"], 3)

    def test_api_check_result(self):
        # ============save check result===========
        data = {
            "check_results": [
                {
                    "username": "test",
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"log", "label": {"mode": "irq"}}],
                    "start": 1,
                    "end": 7,
                    "check_item": "cpu_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                },
                {
                    "username": "test",
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 2,
                    "end": 7,
                    "check_item": "mem_usage",
                    "condition": "xxx",
                    "value": "No data"
                },
                {
                    "username": "test",
                    "host_id": "id2",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 5,
                    "end": 9,
                    "check_item": "disk_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                },
                {
                    "username": "test",
                    "host_id": "id2",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq", "a": 1}}, {"name": 2}],
                    "start": 15,
                    "end": 22,
                    "check_item": "disk_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                },
                {
                    "username": "test",
                    "host_id": "id3",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq", "a": 1}}, {"name": 2}],
                    "start": 15,
                    "end": 22,
                    "check_item": "disk_usage",
                    "condition": "xxx",
                    "value": "No data"
                }
            ]
        }
        res = self.proxy.save_check_result(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        data = {
            "check_results":[
                {
                    "username": "test",
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 2,
                    "end": 7,
                    "check_item": "mem_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                },
                {
                    "username": "test",
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 8,
                    "end": 10,
                    "check_item": "cpu_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                }
            ]
        }
        res = self.proxy.save_check_result(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        # ============get check result==============
        # sort by check_item
        data = {
            "username": "test",
            "time_range": [6, 14],
            "check_items": [],
            "host_list": [],
            "sort": "check_item",
            "direction": "desc",
            "page": 1,
            "per_page": 2
        }
        expected_res = {
            "total_page": 2,
            "total_count": 4,
            "check_result": [
                {
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 2,
                    "end": 7,
                    "check_item": "mem_usage",
                    "condition": "xxx",
                    "value": "Abnormal",
                    "host_id": "id1",
                },
                {
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 5,
                    "end": 9,
                    "check_item": "disk_usage",
                    "condition": "xxx",
                    "value": "Abnormal",
                    "host_id": "id2",
                }
            ]
        }
        res = self.proxy.get_check_result(data)
        self.assertEqual(res[1], expected_res)
        # sort by start
        data = {
            "username": "test",
            "time_range": [6, 25],
            "check_items": ["cpu_usage", "disk_usage"],
            "host_list": ["id1"],
            "sort": "start",
            "page": 1,
            "per_page": 2
        }
        expected_res = {
            "total_page": 1,
            "total_count": 2,
            "check_result": [
                {
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"log", "label": {"mode": "irq"}}],
                    "start": 1,
                    "end": 7,
                    "check_item": "cpu_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                },
                {
                    "host_id": "id1",
                    "data_list": [{"name": "a", "type":"kpi", "label": {"mode": "irq"}}],
                    "start": 8,
                    "end": 10,
                    "check_item": "cpu_usage",
                    "condition": "xxx",
                    "value": "Abnormal"
                }
            ]
        }
        res = self.proxy.get_check_result(data)
        self.assertEqual(res[1], expected_res)

        data = {
            "username": "test",
            "time_range": [],
            "check_items": [],
            "host_list": []
        }
        res = self.proxy.get_check_result(data)
        self.assertEqual(5, len(res[1]['check_result']))

        # ============delete check result=============
        data = {
            "username": "test",
            "host_list": ["id2"],
            "time_range": [4, 9]
        }
        res = self.proxy.delete_check_result(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)

        # =============get check result count=================
        data = {
            "username": "test",
            "sort": "count",
            "direction": "desc",
            "page": 1,
            "per_page": 2
        }
        expected_res = {
            "results": [
                {
                    "host_id": "id1",
                    "count": 3
                },
                {
                    "host_id": "id2",
                    "count": 1
                }
            ],
            "total_count": 2,
            "total_page": 1
        }
        res = self.proxy.get_check_result_count(data)
        self.assertEqual(res[1], expected_res)
