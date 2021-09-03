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
Date: 2021/8/27 15:06
docs: test_check_timmer.py
description: test check timer
"""
import unittest
import time
from adoctor_check_scheduler.check_scheduler.check_timer import check_time_keeper


class TestGetHostList(unittest.TestCase):
    def test_get_forward_time_range(self):
        time_range1 = check_time_keeper.get_forward_time_range()
        time.sleep(1)
        time_range2 = check_time_keeper.get_forward_time_range()
        self.assertEqual(time_range1[1],time_range2[0])

    def test_get_backward_time_range(self):
        time_range1 = check_time_keeper.get_backward_time_range()
        time_range2 = check_time_keeper.get_backward_time_range()
        self.assertEqual(time_range1[0],time_range2[1])
        check_time_keeper._min_time_stamp = time_range2[0]
        self.assertIsNone(check_time_keeper.get_backward_time_range())
