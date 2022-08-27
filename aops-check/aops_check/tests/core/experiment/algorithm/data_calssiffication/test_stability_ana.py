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
"""
Time:
Author:
Description:
"""
import unittest
from aops_check.core.experiment.algorithm.data_classification.stability_ana import StabilityAnalyzer


class TestStabilityAnalyzer(unittest.TestCase):
    """
    test algorithm ewma
    """

    def test_calculate_should_return_stable_data_when_input_data_is_stable(self):
        stability_analyzer = StabilityAnalyzer()
        data_list = [[1658913069, '0.00002582'],
                     [1658913084, '0.00002582'],
                     [1658913099, '0.00002582'],
                     [1658913114, '0.00002738'],
                     [1658913129, '0.00002738']]

        res = stability_analyzer.calculate(data_list * 10)
        self.assertEqual(res, "stable")

    def test_calculate_should_return_unstable_data_when_input_data_is_unstable(self):
        stability_analyzer = StabilityAnalyzer()
        data_list = [[1658913069, '0.00002582'],
                     [1658913084, '0.00002582'],
                     [1658913099, '0.00002582'],
                     [1658913114, '0.00002738'],
                     [1658913129, '0.00002738'],
                     [1658913069, '100.00002582'],
                     [1658913084, '100.00002582'],
                     [1658913099, '100.00002582'],
                     [1658913114, '100.00002738'],
                     [1658913129, '100.00002738']]

        res = stability_analyzer.calculate(data_list)
        self.assertEqual(res, "unstable")


if __name__ == '__main__':
    unittest.main()
