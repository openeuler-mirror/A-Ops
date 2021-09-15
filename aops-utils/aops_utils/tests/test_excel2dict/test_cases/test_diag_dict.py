#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Test excel2dict for diag
"""
import json
import os
import unittest
import pathlib
from aops_utils.excel2dict.diag_tree_dict import generate_tree_dict, PaintingRuleError


__here__ = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(__here__, "../data/data_for_diag")


class TestRightTree(unittest.TestCase):
    """
    Test if right trees' excels can be converted into correct json files.
    """

    def test_right_tree(self):
        """
        Test if generated json files equal to correct json files.
        Returns:

        """
        for file_name in os.listdir(data_path):
            if file_name.startswith("right_tree") and file_name.endswith("xlsx"):
                excel_path = os.path.join(data_path, file_name)
                tree_dict = generate_tree_dict(excel_path)
                json_name = "".join(file_name.split(".")[:-1]) + ".json"

                with open(os.path.join(data_path, json_name)) as load_f:
                    load_dict = json.load(load_f)
                self.assertTrue(pathlib.Path(json_name))
                self.assertDictEqual(tree_dict, load_dict)


class TestWrongTree(unittest.TestCase):
    """
    Test if some wrong format can be detected during the conversion
    """
    def test_wrong_tree(self):
        """
        Test if some wrong format can be detected during the conversion
        Returns:

        """
        for file_name in os.listdir(data_path):
            if file_name.startswith("wrong_tree") and file_name.endswith("xlsx"):
                excel_path = os.path.join(data_path, file_name)
                with self.assertRaises(PaintingRuleError):
                    generate_tree_dict(excel_path)
