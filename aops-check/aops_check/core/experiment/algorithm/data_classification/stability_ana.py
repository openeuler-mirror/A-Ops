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

from statsmodels.tsa.stattools import adfuller
from aops_check.core.experiment.algorithm import Algorithm


class StabilityAnalyzer(Algorithm):
    """
    Determine if a piece of data is stable
    """

    def __init__(self, threshold=None):
        self._threshold = threshold if threshold else 0.05

    def calculate(self, data: list) -> str:
        """
        Calculate whether a piece of data is stable
        Args:
            data: single item data with timestamp,
                  like [[1658544527, '100'], [1658544527, '100']...]

        Returns:
            str: stable/unstable/unkown
        """
        data_list = []
        for single_data in data:
            data_list.append(float(single_data[1]))

        ret = adfuller(data_list)
        if not ret:
            return "unkown"
        pvalue = ret[1]
        if pvalue < self._threshold:
            return "stable"
        return "unstable"
