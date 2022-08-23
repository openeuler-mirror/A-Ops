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
from typing import Optional, Dict

import pandas as pd

from aops_check.core.experiment.algorithm.base_algo import BaseSingleItemAlgorithm


class Mae(BaseSingleItemAlgorithm):

    def __init__(self, var_times: float = 0.25, window: int = 5) -> None:
        self._var_times = var_times
        self._window = window

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "mae",
            "field": "singlecheck",
            "description": "It's a single item check method using mae algorithm.",
            "path": "aops_check.core.experiment.algorithm.single_item_check.mae.Mae"
        }
        return data

    def calculate(self, data: list, time_range: Optional[list] = None) -> list:
        """
        overload the calculate function
        Args:
            data: single item data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
            time_range: time range of checking. only error found in this range could be record

        Returns:
            list: abnormal data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
        """
        if not data:
            return []
        self.preprocess(data)

        data = pd.DataFrame(data)
        data_time = data[0]
        data_value = data[1]

        mae_value = pd.Series(data_value).rolling(window=self._window).mean()

        ewma_var = self._calculate_variance(data_value, mae_value)
        var_delta = ewma_var * self._var_times

        abnormal_data = []

        for index in mae_value.index:
            if mae_value[index] - var_delta <= data_value[index] <= mae_value[index] + var_delta:
                continue
            if not time_range:
                abnormal_data.append([data_time[index], data_value[index]])
                continue
            if time_range[0] < data_time[index] < time_range[1]:
                abnormal_data.append([data_time[index], data_value[index]])

        return abnormal_data

    @staticmethod
    def _calculate_variance(data: list, moving_average: pd.core.series.Series):
        variance = 0
        flag_list = moving_average.isnull()
        count = 0
        for index in range(len(data)):
            if flag_list[index]:
                count += 1
                continue
            variance += (data[index] - moving_average[index]) ** 2
        variance /= (len(data) - count+1)
        return variance
