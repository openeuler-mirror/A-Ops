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
import json
import time
import unittest

from aops_database.proxy.diag import DiagDatabase
from aops_database.conf.constant import DIAG_TREE_INDEX, DIAG_REPORT_INDEX
from aops_database.factory.mapping import MAPPINGS
from aops_utils.restful.status import SUCCEED
from aops_utils.compare import compare_two_object


class TestDiagDatabase(unittest.TestCase):
    def setUp(self):
        # create engine to database
        host = "127.0.0.1"
        port = 9200
        self.proxy = DiagDatabase(host, port)
        self.proxy.connect()
        self.proxy.delete_index(DIAG_TREE_INDEX)
        self.proxy.delete_index(DIAG_REPORT_INDEX)
        self.proxy.create_index(DIAG_TREE_INDEX, MAPPINGS[DIAG_TREE_INDEX])
        self.proxy.create_index(DIAG_REPORT_INDEX, MAPPINGS[DIAG_REPORT_INDEX])

    def tearDown(self):
        self.proxy.delete_index(DIAG_TREE_INDEX)
        self.proxy.delete_index(DIAG_REPORT_INDEX)
        self.proxy.close()

    def test_api_diag_tree(self):
        # ==============import diag tree===================
        data = {
            "username": "test",
            "trees": [
                {
                    "tree_name": "tree1",
                    "tree_content": {
                        "node1": 3,
                        "node2": 4
                    },
                    "description": "t2",
                    "tag": ["内核", "重启"]
                },
                {
                    "tree_name": "tree2",
                    "tree_content": {
                        "node1": 32,
                        "node2": 41
                    },
                    "description": "t22",
                    "tag": ["CPU"]
                },
                {
                    "tree_name": "tree3",
                    "tree_content": {
                        "node1": 32,
                        "node2": {
                            "a": [1, 2]
                        }
                    },
                    "description": "t22"
                },
                {
                    "tree_name": "tree4",
                    "tree_content": {
                        "node1": 32,
                        "node2": {
                            "a": 1
                        }
                    },
                    "description": "t22"
                }
            ]
        }
        res = self.proxy.import_diag_tree(data)
        self.assertEqual(len(res[1]["succeed_list"]), 4)
        time.sleep(1)
        # =========delete diag tree=====================
        data = {
            "tree_list": ["tree4"],
            "username": "test"
        }
        res = self.proxy.delete_diag_tree(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        # ============get diag tree=====================
        data = {
            "tree_list": [],
            "username": "test"
        }
        res = self.proxy.get_diag_tree(data)
        self.assertEqual(len(res[1]["trees"]), 3)

    def test_api_diag_report(self):
        # =============save diag report===============
        data = {
            "reports": [
                {
                    "username": "test",
                    "host_id": "id1",
                    "tree_name": "tree1",
                    "task_id": "t1",
                    "report_id": "id1",
                    "start": 12,
                    "end": 14,
                    "report": json.dumps({"a":1, "b":2})
                },
                {
                    "username": "test",
                    "host_id": "id2",
                    "tree_name": "tree1",
                    "task_id": "t1",
                    "report_id": "id2",
                    "start": 14,
                    "end": 17,
                    "report": json.dumps({"a":{"b":1}})
                },
                {
                    "username": "test",
                    "host_id": "id1",
                    "tree_name": "tree2",
                    "task_id": "t1",
                    "report_id": "id3",
                    "start": 19,
                    "end": 23,
                    "report": json.dumps({"a":[2,3]})
                },
                {
                    "username": "test",
                    "host_id": "id3",
                    "tree_name": "tree1",
                    "task_id": "t2",
                    "report_id": "id4",
                    "start": 1,
                    "end": 5,
                    "report": json.dumps({"c":4})
                },
                {
                    "username": "test",
                    "host_id": "id3",
                    "tree_name": "tree1",
                    "task_id": "t2",
                    "report_id": "id5",
                    "start": 1,
                    "end": 5,
                    "report": json.dumps({"a": {"2":1}})
                }
            ]
        }
        res = self.proxy.save_diag_report(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        # =========get diag report list==============
        data = {
            "username": "test",
            "time_range": [1, 20],
            "host_list": ["id1", "id2", "id3"],
            "tree_list": ["tree1", "tree2"],
            "sort": "start",
            "direction": "desc",
            "page": 1,
            "per_page": 2
        }
        expected_res = {
            "total_count": 5,
            "total_page": 3,
            "result": [
                {
                    "host_id": "id1",
                    "tree_name": "tree2",
                    "task_id": "t1",
                    "report_id": "id3",
                    "start": 19,
                    "end": 23
                },
                {
                    "host_id": "id2",
                    "tree_name": "tree1",
                    "task_id": "t1",
                    "report_id": "id2",
                    "start": 14,
                    "end": 17
                }
            ]
        }
        res = self.proxy.get_diag_report_list(data)
        self.assertEqual(res[1], expected_res)

        # ==========get diag process=================
        data = {
            "username": "test",
            "task_list": ["t1", "t2"]
        }
        expected_res = {
            "result": [
                {
                    "task_id": "t1",
                    "progress": 3
                },
                {
                    "task_id": "t2",
                    "progress": 2
                }
            ]
        }
        res = self.proxy.get_diag_process(data)
        self.assertTrue(compare_two_object(res[1], expected_res))

        # ==========delete diag report==================
        data = {
            "username": "test",
            "report_list": ["id1"]
        }
        self.proxy.delete_diag_report(data)
        time.sleep(1)
        res = self.proxy.get_diag_report(data)
        self.assertEqual(len(res[1]['result']), 0)

        data = {
            "username": "test",
            "report_list": ["id2", "id3"]
        }
        expected_res = {
            "result": [
                {
                    "host_id": "id2",
                    "tree_name": "tree1",
                    "task_id": "t1",
                    "report_id": "id2",
                    "start": 14,
                    "end": 17,
                    "report": {"a":{"b":1}}
                },
                {
                    "host_id": "id1",
                    "tree_name": "tree2",
                    "task_id": "t1",
                    "report_id": "id3",
                    "start": 19,
                    "end": 23,
                    "report": {"a":[2,3]}
                },
            ]
        }
        res = self.proxy.get_diag_report(data)
        self.assertTrue(compare_two_object(expected_res, res[1]))
