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
import unittest

from aops_utils.preprocessing.alignment import *


class TestAlign(unittest.TestCase):

    def test_get_primary_data(self):
        data = {"key1":[[1, 5], [2, 4]], "key2":[[1, 4]]}
        primary = get_primary_data(data)
        self.assertEqual(primary, "key2")

    def test_make_time_series(self):
        period = 5
        time_range = [1, 13]
        data = [[2, 5], [4, 3], [16, 4]]
        time_series = make_time_series(period, time_range, data)
        expected_res = [2, 7, 12]
        self.assertEqual(time_series, expected_res)

    def test_handle_right_boundary(self):
        time_index = 3
        time_series = [1, 6, 11, 16, 21]
        column = [[10, 5], [12, 4]]
        column_res = []
        handle_right_boundary(time_index, time_series, column, column_res)
        expected_res = [[16, 4], [21, 4]]
        self.assertEqual(column_res, expected_res)

    def test_get_cur_value(self):
        column = [[1, 5], [4, 3]]
        pos = 0
        cur_time = 3
        cur_value = get_cur_value(pos, column, cur_time)
        self.assertEqual(cur_value, 5)
        pos = 1
        cur_value = get_cur_value(pos, column, cur_time)
        self.assertEqual(cur_value, 3)
        cur_time = 2
        cur_value = get_cur_value(pos, column, cur_time)
        self.assertEqual(cur_value, 5)

    def test_align_certain_data(self):
        time_series = [1, 5, 9, 13, 17]
        column = [[1, 5], [3, 7], [8, 1], [20, 3]]
        expected_res = [[1, 5], [5, 7], [9, 1], [13, 1], [17, 3]]
        column_res = align_certain_data(time_series, column)
        self.assertEqual(expected_res, column_res)

    def test_align(self):
        period = 5
        time_range = [1, 12]
        data = {
            "key1": [[1, 3], [3, 5], [7, 1], [15, 2]]
        }
        res = align(period, time_range, data)
        expected_res = {
            "key1": [[1, 3], [6, 1], [11, 2]]
        }
        self.assertEqual(res, expected_res)
