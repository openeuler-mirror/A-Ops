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
from typing import Dict, List


METRIC_MODEL_MAP = {
    "default_model": "NSigma-1",  # NSigma model
    "model_info": {
        "cpu_load15": "NSigma-1",  # NSigma model
        "rx_error": "NSigma-1"  # NSigma model
    }
}

SCENE_MODEL_MAP = {
    "default_model": "StatisticalCheck-1",  # StatisticalCheck
    "model_info": {
        "big_data": "StatisticalCheck-1",  # StatisticalCheck
        "web": "StatisticalCheck-1",  # StatisticalCheck
        "edge": "StatisticalCheck-1",  # StatisticalCheck
        "cloud": "StatisticalCheck-1",  # StatisticalCheck
    }
}


class ModelAssign:
    """
    assign model of collected metric(kpi)
    """

    @staticmethod
    def assign_kpi_model_by_name(metric_model_map: dict = None) -> Dict[str, str]:
        """
        assign single item check model by metrics' name
        Args:
            metric_model_map: metric and model matching relationship
                e.g.
                {
                    "default_model": "NSigma-1",  # NSigma model
                    "model_info": {
                        "cpu_load15": "NSigma-1",  # NSigma model
                        "rx_error": ""  # if empty, use default model
                    }
                }

        Raises:
            ValueError
        """
        if metric_model_map is None:
            metric_model_map = METRIC_MODEL_MAP
        if "default_model" not in metric_model_map:
            raise ValueError("A 'default_model' should be given for metric with empty model id.")

        default_model_info = metric_model_map["default_model"]
        model_info = metric_model_map.get("model_info", {})

        assign_model = {}
        for metric in model_info.keys():
            if model_info[metric]:
                assign_model[metric] = model_info[metric]
            else:
                assign_model[metric] = default_model_info

        return assign_model

    @staticmethod
    def assign_kpi_model_by_waveform(data_values: Dict[str, list]):
        """
        assign single check item check model by metrics' waveform
        """
        pass

    @staticmethod
    def assign_multi_kpi_model(scene: str, scene_model_map: Dict = None) -> str:
        """
        assign multi item check model by scene
        Args:
            scene: host's scene
            scene_model_map: scene and model's matching model
        Raises:
            ValueError
        """
        if scene_model_map is None:
            scene_model_map = SCENE_MODEL_MAP
        if "default_model" not in scene_model_map:
            raise ValueError("A 'default_model' should be given in case of no scene matches.")

        model_info = scene_model_map.get("model_info", {})
        return model_info.get(scene, scene_model_map["default_model"])

    @staticmethod
    def assign_cluster_diag_model() -> str:
        return "StatisticDiag-1"
