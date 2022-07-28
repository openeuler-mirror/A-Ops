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

from aops_check.core.experiment.algorithm.built_in_algo.mae import Mae


class TestMae(unittest.TestCase):
    """
    test algorithm mae
    """
    def test_calculate_should_return_error_data_when_input_data_has_error(self):
        algorithm = Mae()
        data = [[1,1],[2,2],[3,3],[4,1],[5,2],[6,3],[7,1],[8,2],[9,3],[10,1],[11,2],[12,10],[13,1],[14,2]]
        res = algorithm.calculate(data)
        self.assertEqual(res, [[1,1],[2,2],[3,3],[4,1],[12,10],[13,1]])

    def test_calculate_should_return_empty_list_when_input_data_has_error_beyond_time_range(self):
        algorithm = Mae()
        data = [[1,1],[2,2],[3,3],[4,1],[5,2],[6,3],[7,1],[8,2],[9,3],[10,1],[11,2],[12,10],[13,1],[14,2]]
        res = algorithm.calculate(data, [12, 14])
        self.assertEqual(res, [[13,1]])

    def test_calculate_should_return_empty_list_when_input_data_is_normal(self):
        algorithm = Mae()
        data = [[1,1],[2,2],[3,3],[4,4],[5,1],[6,2],[7,3],[8,4],[9,1],[10,2],[11,3],[12,4],[13,1],[14,2]]
        res = algorithm.calculate(data)
        # should optimize the algorithm
        self.assertEqual(res, data)
