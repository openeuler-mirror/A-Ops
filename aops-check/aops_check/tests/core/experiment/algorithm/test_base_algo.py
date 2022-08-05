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
from aops_check.core.experiment.algorithm.base_algo import BaseSingleItemAlgorithm, \
    BaseMultiItemAlgorithmOne, BaseMultiItemAlgorithmTwo


class TestBaseSingleItemAlgorithm(unittest.TestCase):
    """
    test base algo class BaseSingleItemAlgorithm
    """

    def test_init_object_should_raise_error_when_calculate_function_wasnt_reloaded(self):
        class NewAlgo(BaseSingleItemAlgorithm):
            pass

        def mock_init_algo_object():
            new_algo = NewAlgo()
            return new_algo

        self.assertRaises(TypeError, mock_init_algo_object)


class TestBaseMultiItemAlgorithmOne(unittest.TestCase):
    """
    test base algo class BaseMultiItemAlgorithmOne
    """

    def test_init_object_should_raise_error_when_calculate_function_wasnt_reloaded(self):
        class NewAlgo(BaseMultiItemAlgorithmOne):
            pass

        def mock_init_algo_object():
            new_algo = NewAlgo()
            return new_algo

        self.assertRaises(TypeError, mock_init_algo_object)


class TestBaseMultiItemAlgorithmTwo(unittest.TestCase):
    """
    test algorithm xgboost
    """

    def test_init_object_should_raise_error_when_calculate_function_wasnt_reloaded(self):
        class NewAlgo(BaseMultiItemAlgorithmTwo):
            pass

        def mock_init_algo_object():
            new_algo = NewAlgo()
            return new_algo

        self.assertRaises(TypeError, mock_init_algo_object)
