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
Date: 2021/9/1 10:22
docs: test_data_backpack.py
description: test data backpack
"""
import unittest
from adoctor_check_executor.check_rule_plugins.expression_parser.data_backpack import DataBackpack
from adoctor_check_executor.common.check_error import CheckPluginError


class TestDataCackPack(unittest.TestCase):
    def setUp(self) -> None:
        data_vector = {
            "$0": [[1630422080.526, '3207113320'], [1630422095.526, '3207113320'],
                   [1630422110.526, '3207113320']],
            "$1": [[1630422082.931, '89588736'], [1630422097.931, '89588736'],
                   [1630422112.931, '89588736']]
        }
        self.data_backpack = DataBackpack("$1", 1, data_vector)

    def test_is_number(self):
        self.assertTrue(DataBackpack._is_number('1'))
        self.assertTrue(DataBackpack._is_number('1.3'))
        self.assertTrue(DataBackpack._is_number('1.37'))
        self.assertTrue(DataBackpack._is_number('-1.37'))
        self.assertTrue(DataBackpack._is_number('1e3'))
        self.assertFalse(DataBackpack._is_number('1m3'))
        self.assertFalse(DataBackpack._is_number('faa'))
        self.assertFalse(DataBackpack._is_number('this is a log piece'))

    def test_get_key_data_name(self):
        self.assertEqual(self.data_backpack.get_key_data_name("default"), "$1")
        self.assertEqual(self.data_backpack.get_key_data_name("$0"), "$0")
        with self.assertRaises(CheckPluginError, msg="Invalid key data name"):
            self.data_backpack.get_key_data_name("$2")

    def test_pre_check(self):
        self.assertTrue(self.data_backpack._pre_check(0, "$1"))
        self.assertFalse(self.data_backpack._pre_check(-1, "$1"))
        self.assertFalse(self.data_backpack._pre_check(4, "$1"))
        self.assertFalse(self.data_backpack._pre_check(-1, "$4"))
        self.assertFalse(self.data_backpack._pre_check(1, "$4"))

    def test_get_time_stamp(self):
        self.assertEqual(self.data_backpack.get_time_stamp(0, "$1"), 1630422082.931)
        with self.assertRaises(CheckPluginError, msg="Invalid key data name or index"):
            self.data_backpack.get_time_stamp(-1, "$1")
            self.data_backpack.get_time_stamp(4, "$1")
            self.data_backpack.get_time_stamp(-1, "$4")
            self.data_backpack.get_time_stamp(1, "$4")


if __name__ == "__main__":
    unittest.main()
