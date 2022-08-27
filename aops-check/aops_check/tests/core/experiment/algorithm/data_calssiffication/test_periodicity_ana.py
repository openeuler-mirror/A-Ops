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
from aops_check.core.experiment.algorithm.data_classification.periodicity_ana import PeriodicityAnalyzer


class TestPeriodicityAnalyzer(unittest.TestCase):
    """
    test algorithm ewma
    """

    def test_calculate_should_return_period_data_when_input_data_has_period(self):
        periodicity_analyzer = PeriodicityAnalyzer(threshold=0.1)
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

        res = periodicity_analyzer.calculate(data_list * 10)
        self.assertDictEqual(res, {'max_acf_score': '0.22000000062399974', 'period': 2, 'is_period': True})

    def test_calculate_should_return_period_data_when_input_data_has_period(self):
        periodicity_analyzer = PeriodicityAnalyzer(threshold=0.1)
        data_list = [[1658913069, '0.00002582'],
                     [1658913084, '0.00002583'],
                     [1658913099, '0.00002584'],
                     [1658913114, '0.00002735'],
                     [1658913129, '0.00002736'],
                     [1658913069, '100.00002582'],
                     [1658913084, '100.00002583'],
                     [1658913099, '100.00002584'],
                     [1658913114, '100.00002735'],
                     [1658913129, '100.00002736']]

        res = periodicity_analyzer.calculate(data_list * 10)
        self.assertDictEqual(res, {'is_period': True, 'max_acf_score': '0.5500000003079998', 'period': 11})

    def test_calculate_should_return_unstable_data_when_input_data_is_unstable(self):
        periodicity_analyzer = PeriodicityAnalyzer(threshold=0.1)
        data_list = [[1658913069, '1'],
                     [1658913084, '2'],
                     [1658913099, '3'],
                     [1658913114, '4'],
                     [1658913129, '5'],
                     [1658913069, '6'],
                     [1658913084, '7'],
                     [1658913099, '8'],
                     [1658913114, '9'],
                     [1658913129, '100.00002738']]

        res = periodicity_analyzer.calculate(data_list)
        self.assertDictEqual(res, {'max_acf_score': '0.011854557211020725', 'period': 2, 'is_period': False})


if __name__ == '__main__':
    unittest.main()
