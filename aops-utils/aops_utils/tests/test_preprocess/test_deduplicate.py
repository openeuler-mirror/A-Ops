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
Date: 2021/9/23 22:01
docs: test_deduplicate.py
description: test deduplicated
"""
import unittest
from aops_utils.preprocessing.deduplicate import *


class TestDeduplicate(unittest.TestCase):
    def test_deduplicate_certain_data(self):
        data_list = []
        self.assertListEqual(deduplicate_certain_data(data_list), [])

        data_list = [[1111, "ttttt"], [1111, "qqqq"], [1112, '55555'], [1112, 'bbb'], [1112, 'bbb'],
                     [1113, "rrrr"], [1114, "ccccc"]]
        ret = deduplicate_certain_data(data_list)
        expect_ret = [[1111, "ttttt qqqq"], [1112, '55555 bbb bbb'], [1113, "rrrr"], [1114, "ccccc"]]
        self.assertListEqual(ret, expect_ret)

    def test_deduplicate(self):
        data_vector = {}
        self.assertDictEqual(deduplicate(data_vector), {})

        data_vector = {"data1": [[1111, "ttttt"], [1111, "qqqq"], [1112, '55555'], [1112, 'bbb'], [1112, 'bbb'],
                                 [1113, "rrrr"], [1114, "ccccc"]],
                       "data2": [],
                       "data3": [[1111, ""], [1111, ""], [1112, '55555'], [1112, 'bbb'], [1112, 'bbb'],
                                 [1113, "rrrr"], [1114, ""]]}
        ret = deduplicate(data_vector)
        expect_ret = {"data1": [[1111, "ttttt qqqq"], [1112, '55555 bbb bbb'], [1113, "rrrr"], [1114, "ccccc"]],
                      "data2": [],
                      "data3": [[1111, " "], [1112, '55555 bbb bbb'], [1113, "rrrr"], [1114, ""]]}
        self.assertDictEqual(ret, expect_ret)
