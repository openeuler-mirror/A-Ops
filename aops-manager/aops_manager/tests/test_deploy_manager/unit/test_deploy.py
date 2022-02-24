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

from aops_manager.database.proxy.deploy import DeployProxy
from aops_manager.conf.constant import TEMPLATE_INDEX, TASK_INDEX
from aops_manager.conf import configuration
from aops_manager.database.factory.mapping import MAPPINGS
from aops_utils.restful.status import SUCCEED, DATA_EXIST
from aops_utils.compare import compare_two_object


class TestDeployDatabase(unittest.TestCase):
    def setUp(self):
        # create engine to database
        host = "127.0.0.1"
        port = 9200
        self.proxy = DeployProxy(configuration, host, port)
        self.proxy.connect()
        self.proxy.delete_index(TEMPLATE_INDEX)
        self.proxy.delete_index(TASK_INDEX)
        self.proxy.create_index(TEMPLATE_INDEX, MAPPINGS[TEMPLATE_INDEX])
        self.proxy.create_index(TASK_INDEX, MAPPINGS[TASK_INDEX])

    def tearDown(self):
        self.proxy.delete_index(TEMPLATE_INDEX)
        self.proxy.delete_index(TASK_INDEX)
        self.proxy.close()

    def test_api_task(self):
        # ==============save task info===================
        data = [
            {
                "username": "aaa",
                "task_id": "aaaa",
                "task_name": "task1",
                "description": "itsss ",
                "template_name": ["1", "2"]
            },
            {
                "username": "aaa",
                "task_id": "cccc",
                "task_name": "task3",
                "description": "itsss ",
                "template_name": ["1", "2"]
            },
            {
                "username": "aaa",
                "task_id": "bbbb",
                "task_name": "task2",
                "description": "itsss ",
                "template_name": []
            },
            {
                "username": "aaa",
                "task_id": "dddd",
                "task_name": "task4",
                "description": "itsss ",
                "template_name": ["1", "2"]
            }
        ]
        for task in data:
            res = self.proxy.add_task(task)
            self.assertEqual(res, SUCCEED)

        time.sleep(1)
        # ===============get task=================
        data = {
            "task_list": ["task1"],
            "username": "b"
        }
        expected_res = {
            "total_count": 0,
            "total_page": 0,
            "task_infos": []
        }
        res = self.proxy.get_task(data)
        self.assertEqual(expected_res, res[1])

        data = {
            "task_list": [],
            "username": "aaa",
            "sort": "task_name",
            "direction": "desc",
            "page": 2,
            "per_page": 3
        }
        expected_res = {
            "total_count": 4,
            "total_page": 2,
            "task_infos": [
                {
                    "task_id": "aaaa",
                    "task_name": "task1",
                    "description": "itsss ",
                    "template_name": ["1", "2"]
                }
            ]
        }
        res = self.proxy.get_task(data)
        self.assertTrue(compare_two_object(expected_res, res[1]))

        # ==================delete task==================
        data = {
            "task_list": ["aaaa"],
            "username": "aaa"
        }
        res = self.proxy.delete_task(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)

        data = {
            "username": "aaa",
            "task_list": []
        }
        res = self.proxy.get_task(data)
        self.assertEqual(len(res[1]['task_infos']), 3)

    def test_api_template(self):
        # ==============add template===================
        data = [
            {
                "username": "aaa",
                "template_name": "a",
                "description": "itsss ",
                "template_content": {
                    "1": 1
                }
            },
            {
                "username": "aaa",
                "template_name": "c",
                "description": "itsss ",
                "template_content": {
                    "1": {"a": 2},
                    "3": 3
                }
            },
            {
                "username": "aaa",
                "template_name": "d",
                "description": "itsss ",
                "template_content": {
                    "4": 4
                }
            },
            {
                "username": "aaa",
                "template_name": "b",
                "description": "itsss ",
                "template_content": {
                    "1": 1,
                    "4": {
                        "a": {
                            "a": [1]
                        }
                    }
                }
            },
        ]
        for template in data:
            res = self.proxy.add_template(template)
            self.assertEqual(res, SUCCEED)

        time.sleep(1)
        # ===============get template=================
        data = {
                "username": "aaa",
                "template_name": "b",
                "description": "itsss ",
                "template_content": {
                    "1": 1}
            }
        res = self.proxy.add_template(data)
        self.assertEqual(res, DATA_EXIST)

        data = {
            "template_list": ["task1"],
            "username": "b"
        }
        expected_res = {
            "total_count": 0,
            "total_page": 0,
            "template_infos": []
        }
        res = self.proxy.get_template(data)
        self.assertEqual(expected_res, res[1])

        data = {
            "template_list": [],
            "username": "aaa",
            "sort": "template_name",
            "direction": "asc",
            "page": 2,
            "per_page": 1
        }
        expected_res = {
            "total_count": 4,
            "total_page": 4,
            "template_infos": [
                {
                    "template_name": "b",
                    "description": "itsss ",
                    "template_content": {
                    "1": 1,
                    "4": {
                        "a": {
                            "a": [1]
                        }
                    }
                }
                }
            ]
        }
        res = self.proxy.get_template(data)
        self.assertTrue(compare_two_object(expected_res, res[1]))

        # ==================delete template==================
        data = {
            "template_list": ["c", "d"],
            "username": "aaa"
        }
        res = self.proxy.delete_template(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)

        data = {
            "username": "aaa",
            "template_list": []
        }
        res = self.proxy.get_template(data)
        self.assertEqual(len(res[1]['template_infos']), 2)
