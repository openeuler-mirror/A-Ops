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
from typing import Dict
from aops_check.core.experiment.algorithm.base_algo import BaseMultiItemAlgorithmTwo


METRIC_WEIGHT_MAP = {
    "default_weight": 0.1,
    "metric_weight": {
        "up": 1,
        "scrape_duration_seconds": 0.5,
        "scrape_samples_post_metric_relabeling": 0.1,
        "scrape_samples_scraped": 0.1,
        "scrape_series_added": 0.1
    }
}


class StatisticalCheck(BaseMultiItemAlgorithmTwo):

    def __init__(self, threshold: float = 1.0, metric_weight_map: dict = None):
        """

        Args:
            threshold: threshold value, if weighted value is bigger than this, assume the host is abnormal
            metric_weight_map: weights and metric name matching relationship
        """
        self.__threshold = threshold
        self.__metric_weight_map = metric_weight_map or METRIC_WEIGHT_MAP

    def calculate(self, data: list) -> bool:
        """
        calculate total weighted value and compare with threshold
        Args:
            data: result of single item check, like [{"metric_name": "m1", "metric_label": "l1"}]

        Returns:
            bool
        """
        weighted_sum = 0
        metric_weight = self.__metric_weight_map["metric_weight"]
        default_weight = self.__metric_weight_map["default_weight"]
        for metric in data:
            metric_name = metric["metric_name"]
            if metric_name in metric_weight:
                weighted_sum += metric_weight[metric_name]
            else:
                weighted_sum += default_weight

        if weighted_sum > self.__threshold:
            return True
        return False

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "statistical_multi_item_check",
            "field": "multicheck",
            "description": "It's a statistical multiple item check method.",
            "path": "aops_check.core.experiment.algorithm.multi_item_check."
                    "statistical_multi_item_check.StatisticalCheck"
        }
        return data
