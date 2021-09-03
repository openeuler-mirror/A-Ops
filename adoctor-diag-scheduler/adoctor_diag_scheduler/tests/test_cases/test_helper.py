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
import unittest
from unittest import mock

from aops_utils.restful.response import MyResponse
from adoctor_diag_scheduler.function.helper import get_time_slices, get_trees_content, \
    get_tree_from_database


class TestHelperOne(unittest.TestCase):
    """
    Test basic functions in helper.py
    """
    def test_get_time_slices(self):
        res1 = get_time_slices([10, 100], 10)
        self.assertEqual(len(res1), 9)

        res2 = get_time_slices([10, 100], 100)
        self.assertEqual(res2, [[10, 100]])

        res2 = get_time_slices([10, 100], 50)
        self.assertEqual(res2, [[10, 60], [60, 100]])

    @mock.patch("adoctor_diag_scheduler.function.helper.get_tree_from_database")
    def test_get_diag_tree_content(self, mock_res_from_database):
        mock_res_from_database.side_effect = [
            {"name": "tree1"}, {}
        ]
        res_dict = get_trees_content(["tree1", "tree2"], "admin")
        expected_res = {"tree1": {"name": "tree1"}}
        self.assertEqual(res_dict, expected_res)

    @mock.patch.object(MyResponse, "get_response")
    def test_get_tree_from_database_1(self, mock_get_tree_responnse):
        mock_get_tree_responnse.return_value = {
            "code": 200,
            "msg": "",
            "trees": [{"tree_name": "tree1",
                       "tree_content": {"name": "test"},
                       "description": "",
                       "tag": []}]
        }
        res = get_tree_from_database("admin", "tree1")
        expected_res = {"name": "test"}
        self.assertEqual(res, expected_res)

    @mock.patch.object(MyResponse, "get_response")
    def test_get_tree_from_database_2(self, mock_get_tree_responnse):
        mock_get_tree_responnse.return_value = {
            "code": 200,
            "msg": "",
            "trees": [{"tree_name": "tree1",
                       "tree_content_miss": {"name": "test"},
                       "description": "",
                       "tag": []}]
        }
        res = get_tree_from_database("admin", "tree1")
        expected_res = {}
        self.assertEqual(res, expected_res)

    @mock.patch.object(MyResponse, "get_response")
    def test_get_tree_from_database_3(self, mock_get_tree_responnse):
        mock_get_tree_responnse.return_value = {
            "code": 200,
            "msg": "",
            "trees": []
        }
        res = get_tree_from_database("admin", "tree1")
        expected_res = {}
        self.assertEqual(res, expected_res)

    @mock.patch.object(MyResponse, "get_response")
    def test_get_tree_from_database_4(self, mock_get_tree_responnse):
        mock_get_tree_responnse.return_value = {
            "code": 500,
            "msg": "",
            "trees": [{"tree_name": "tree1",
                       "tree_content": {"name": "test"},
                       "description": "",
                       "tag": []}]
        }
        res = get_tree_from_database("admin", "tree1")
        expected_res = {}
        self.assertEqual(res, expected_res)
