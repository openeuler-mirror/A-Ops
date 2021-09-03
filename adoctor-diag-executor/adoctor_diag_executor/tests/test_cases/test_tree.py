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

from adoctor_diag_executor.function.diag_tree import DiagTree

__here__ = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(__here__, "../data/")


class TestTree(unittest.TestCase):
    tree_example = os.path.join(data_path, "tree_example.json")
    with open(tree_example, 'r', encoding="UTF-8") as json_file:
        tree_json = json_file.read()
    tree_dict = json.loads(tree_json)
    tree = DiagTree(tree_dict)

    def test_generation(self):
        leaves_set = {'check_item2', 'check_item3', 'check_item9', 'check_item6',
                      'check_item8', 'check_item4', 'check_item5', 'check_item1',
                      'check_item7'}

        self.assertEqual(TestTree.tree.check_items, leaves_set)

    def test_diagnose(self):
        check_result = {
            "abnormal": {"check_item1", "check_item3", "check_item6", "check_item9"},
            "normal": {"check_item2", "check_item4"},
            "no data": {"check_item5", "check_item8"},
            "internal error": "check_item7"
        }

        TestTree.tree.diagnose(check_result)

        tree_example_diagnosed = os.path.join(data_path, "tree_example_diagnosed.json")
        with open(tree_example_diagnosed, 'r', encoding="UTF-8") as json_file:
            diagnosed_json = json_file.read()
            diagnosed_tree_dict = json.loads(diagnosed_json)

        self.assertEqual(TestTree.tree.to_dict(), diagnosed_tree_dict)
