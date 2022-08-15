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

import numpy as np

from aops_check.core.experiment.algorithm.base_algo import BaseSingleItemAlgorithm


class NSigma(BaseSingleItemAlgorithm):

    def __init__(self, n: int = 3):
        self._n = n

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "ngisgma",
            "field": "singlecheck",
            "description": "It's a single item check method using nsigma algorithm.",
            "path": "aops_check.core.experiment.algorithm.single_item_check.nsigma.Nsigma"
        }
        return data

    def calculate(self, data: list, time_range: Optional[list] = None) -> list:
        """
        overload calculate function
        Args:
            data: single item data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
            time_range: time range of checking. only error found in this range could be record
        Returns:
            list: abnormal data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
        """
        data_time = []
        data_value = []

        for single_data in data:
            data_time.append(single_data[0])
            data_value.append(single_data[1])

        ymean = np.mean(data_value)
        ystd = np.std(data_value)
        threshold1 = ymean - self._n * ystd
        threshold2 = ymean + self._n * ystd

        abnormal_data = []

        for index in range(0, len(data_value)):
            if not (data_value[index] < threshold1) | (data_value[index] > threshold2):
                continue
            if not time_range:
                abnormal_data.append([data_time[index], data_value[index]])
                continue
            if time_range[0] < data_time[index] < time_range[1]:
                abnormal_data.append([data_time[index], data_value[index]])

        return abnormal_data
