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
from aops_check.core.rule.model_assign import ModelAssign


class TestAssignSingleKpiModelByName(unittest.TestCase):
    """
    test assign model by kpi name
    """

    def test_assign_should_return_normal_when_input_metrics_all_in_builtin_map(self):
        model_assign = ModelAssign()
        assigned_model = model_assign.assign_kpi_model_by_name(["cpu_load15", "rx_error"])
        self.assertDictEqual(assigned_model, {"cpu_load15": "NSigma-1", "rx_error": "NSigma-1"})

    def test_assign_should_return_normal_when_input_some_metrics_not_in_builtin_map(self):
        model_assign = ModelAssign()
        assigned_model = model_assign.assign_kpi_model_by_name(["cpu_load1", "rx_error"])
        self.assertDictEqual(assigned_model, {"rx_error": "NSigma-1"})

    def test_assign_should_return_normal_when_given_map_with_default_model(self):
        model_assign = ModelAssign()

        user_defined_map = {
            "default_model": "NSigma-1",
            "model_info": {
                "cpu_load15": "NSigma-1",
                "rx_error": ""
            }
        }
        assigned_model = model_assign.assign_kpi_model_by_name(["cpu_load15", "rx_error",
                                                                "cpu_load1"], user_defined_map)
        self.assertDictEqual(assigned_model, {"cpu_load15": "NSigma-1", "rx_error": "NSigma-1"})

    def test_assign_should_raise_value_error_when_default_model_not_given(self):
        model_assign = ModelAssign()
        user_defined_map = {
            "model_info": {
                "cpu_load15": "Mae-1",
                "rx_error": "NSigma-1"
            }
        }
        self.assertRaises(ValueError, model_assign.assign_kpi_model_by_name,
                          ["cpu_load1", "rx_error"], user_defined_map)


class TestAssignMultiKpiModelByName(unittest.TestCase):
    def test_assign_should_return_normal_when_input_scene_in_builtin_map(self):
        model_assign = ModelAssign()
        assigned_model = model_assign.assign_multi_kpi_model("big_data")
        self.assertEqual(assigned_model, "StatisticalCheck-1")

    def test_assign_should_return_normal_when_input_scene_not_in_builtin_map(self):
        model_assign = ModelAssign()
        assigned_model = model_assign.assign_multi_kpi_model("test")
        self.assertEqual(assigned_model, "StatisticalCheck-1")

    def test_assign_should_return_normal_when_given_map_with_default_model(self):
        model_assign = ModelAssign()
        user_defined_map = {
            "default_model": "StatisticalCheck-1",
            "model_info": {
                "big_data": "new_model",
                "web": "StatisticalCheck-1",
                "edge": "StatisticalCheck-1",
                "cloud": "StatisticalCheck-1",
            }
        }
        assigned_model = model_assign.assign_multi_kpi_model("big_data", user_defined_map)
        self.assertEqual(assigned_model, "new_model")

    def test_assign_should_raise_value_error_when_given_map_without_default_model(self):
        model_assign = ModelAssign()
        user_defined_map = {
            "model_info": {
                "big_data": "new_model",
                "web": "StatisticalCheck-1",
                "edge": "StatisticalCheck-1",
                "cloud": "StatisticalCheck-1",
            }
        }
        self.assertRaises(ValueError, model_assign.assign_multi_kpi_model, "big_data", user_defined_map)
