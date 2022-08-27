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
from aops_check.core.experiment.algorithm.data_classification.trend_ana import TrendAnalyzer


class TestTrendAnalyzer(unittest.TestCase):
    """
    test algorithm ewma
    """

    def test_calculate_should_return_no_trend_data_when_input_data_has_no_trend(self):
        trendc_analyzer = TrendAnalyzer(threshold=0.1)
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

        res = trendc_analyzer.calculate(data_list * 10)
        self.assertEqual(res, "no trend")

    def test_calculate_should_return_increasing_data_when_input_data_has_increase_trend(self):
        trendc_analyzer = TrendAnalyzer(threshold=0.1)
        data_list = [[1658913069, '1.00002582'],
                     [1658913084, '2.00002582'],
                     [1658913099, '3.00002582'],
                     [1658913114, '4.00002738'],
                     [1658913129, '5.00002738'],
                     [1658913069, '6.00002582'],
                     [1658913084, '7.00002582'],
                     [1658913099, '8.00002582'],
                     [1658913114, '9.00002738'],
                     [1658913129, '10.00002738']]

        res = trendc_analyzer.calculate(data_list)
        self.assertEqual(res, "increasing")

    def test_calculate_should_return_decreasing_data_when_input_data_has_descrease_trend(self):
        trendc_analyzer = TrendAnalyzer(threshold=0.1)
        data_list = [[1658913069, '91.00002582'],
                     [1658913084, '82.00002582'],
                     [1658913099, '73.00002582'],
                     [1658913114, '64.00002738'],
                     [1658913129, '55.00002738'],
                     [1658913069, '46.00002582'],
                     [1658913084, '37.00002582'],
                     [1658913099, '28.00002582'],
                     [1658913114, '19.00002738'],
                     [1658913129, '10.00002738']]

        res = trendc_analyzer.calculate(data_list)
        self.assertEqual(res, "decreasing")


if __name__ == '__main__':
    unittest.main()
