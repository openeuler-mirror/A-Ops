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
from typing import Optional
import pandas as pd
from scipy import stats
from aops_check.core.experiment.algorithm import Algorithm


class TrendAnalyzer(Algorithm):
    """
    Determine if a piece of data has a trend
    """

    def __init__(self, threshold: Optional[float] = None):
        """
        Constructor
        Args:
            threshold: threshold of cdf p_value
        """
        self._threshold = threshold if threshold else 0.05

    def calculate(self, data: list) -> str:
        """
        Calculate whether a piece of data has trend
        Args:
            data: single item data with timestamp,
                  like [[1658544527, '100'], [1658544527, '100']...]

        Returns:
            str: 'increasing' or 'decreasing' or 'no trend'
        """
        data_list = []
        for single_data in data:
            data_list.append(float(single_data[1]))
        data_len = len(data_list)
        if data_len % 2 == 1:
            del data_list[int((data_len - 1) / 2)]
        span_len = int(data_len / 2)
        positive_num = negative_num = 0
        for i in range(span_len):
            diff = data_list[i + span_len] - data_list[i]
            if diff > 0:
                positive_num += 1
            elif diff < 0:
                negative_num += 1
            else:
                continue
        num = positive_num + negative_num
        k = min(positive_num, negative_num)
        p_value = 2 * stats.binom.cdf(k, num, 0.5)
        if positive_num > negative_num and p_value < self._threshold:
            return 'increasing'
        if negative_num > positive_num and p_value < self._threshold:
            return 'decreasing'
        return 'no trend'
