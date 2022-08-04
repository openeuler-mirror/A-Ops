#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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

from aops_check.core.experiment.algorithm.built_in_algo.nsigma import NSigma


class TestNSigma(unittest.TestCase):
    """
    test algorithm Nsigma
    """
    def test_calculate_should_return_error_data_when_input_data_has_error(self):
        algorithm = NSigma(3)
        data = [[1,1],[2,1],[3,1],[4,1],[5,1],[6,100],[7,100],[8,2000],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1]]
        res = algorithm.calculate(data)
        self.assertEqual(res, [[8, 2000]])

    def test_calculate_should_return_empty_list_when_input_data_has_error_beyond_time_range(self):
        algorithm = NSigma(3)
        data = [[1,1],[2,1],[3,1],[4,1],[5,1],[6,100],[7,100],[8,2000],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1]]
        res = algorithm.calculate(data, [12, 14])
        self.assertEqual(res, [])

    def test_calculate_should_return_empty_list_when_input_data_is_normal(self):
        algorithm = NSigma(3)
        data = [[1,1],[2,1],[3,1],[4,1],[5,1],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1]]
        res = algorithm.calculate(data)
        self.assertEqual(res, [])
