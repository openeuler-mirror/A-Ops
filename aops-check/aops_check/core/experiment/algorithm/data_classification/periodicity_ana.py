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
import datetime
from typing import Optional
import numpy as np
from scipy.fftpack import fftfreq
from statsmodels.tsa.stattools import acf
from aops_check.core.experiment.algorithm import Algorithm

default_preset_period = [{"unit": "minutes", "value": 30},
                         {"unit": "hours", "value": 1},
                         {"unit": "hour", "value": 12},
                         {"unit": "days", "value": 1}]


class PeriodicityAnalyzer(Algorithm):
    """
    Determine if a piece of data has a trend
    """

    def __init__(self, threshold: Optional[float] = None,
                 top_k: Optional[float] = None,
                 step: Optional[dict] = None,
                 preset_period: Optional[int] = None):
        """
        Constructor
        Args:
            dtw_threshold: threshold of dtw
        """
        self._threshold = threshold if threshold else 0.5
        self._top_k = top_k if top_k else 3
        self._step = step if step else {"unit": "seconds", "value": 30}
        self._preset_period_list = preset_period if preset_period else default_preset_period

    def _cal_top_k_period(self, fft_series: np.ndarray) -> np.ndarray:
        """
        Get top k period
        Args:
            time_param(dict): { "unit": "sceonds", "values":111}

        Returns:
            datetime.timedelta/None
        """
        power = np.absolute(fft_series)
        sample_freq = fftfreq(fft_series.size)

        pos_mask = np.where(sample_freq > 0)
        freqs = sample_freq[pos_mask]
        powers = power[pos_mask]

        top_k_idex = np.argpartition(powers, -self._top_k)[-self._top_k:]
        fft_periods = (1 / freqs[top_k_idex]).astype(int)
        return fft_periods

    @staticmethod
    def _get_timedelta(time_param: dict) -> Optional[datetime.timedelta]:
        """
        Get time delta of config
        Args:
            time_param(dict): { "unit": "sceonds", "values":111}

        Returns:
            datetime.timedelta/None
        """
        value = time_param.get("value")
        unit = time_param.get("unit")
        if unit == "seconds":
            return datetime.timedelta(seconds=value)
        if unit == "hours":
            return datetime.timedelta(hours=value)
        if unit == "days":
            return datetime.timedelta(days=value)
        if unit == "weeks":
            return datetime.timedelta(weeks=value)

        return None

    def _get_expected_lags(self):
        """
        Get expected period lags

        Returns:
            list: expected period lags
        """
        lags_list = []
        step_timedelta = PeriodicityAnalyzer._get_timedelta(self._step)
        if not step_timedelta:
            return 0, 0
        for preset_period in self._preset_period_list:
            preset_period_timedelta = PeriodicityAnalyzer._get_timedelta(preset_period)
            if not preset_period_timedelta:
                continue
            lags_list.append(PeriodicityAnalyzer._get_timedelta(preset_period) / step_timedelta)
        expected_lags = np.array(lags_list).astype(int)
        return expected_lags

    def cal_acf_score(self, fft_series: np.ndarray, fft_periods: np.ndarray) -> tuple:
        """
        Calculate acf score of provided periods
        Args:
            fft_series(np.ndarray): data series
            fft_periods(np.ndarray): top k periods list

        Returns:
            tuple: max acf score, period of speculation
        """
        max_acf_score = float("-inf")
        period = 0

        for lag in fft_periods:
            acf_score = acf(fft_series, nlags=lag)[-1]
            if acf_score > max_acf_score:
                period = lag
                max_acf_score = acf_score

        expected_lags = self._get_expected_lags()
        for lag in expected_lags:
            acf_score = acf(fft_series, nlags=lag, fft=False)[-1]
            if acf_score > max_acf_score:
                period = lag
                max_acf_score = acf_score

        return max_acf_score, period

    def calculate(self, data: list) -> dict:
        """
        Calculate whether a piece of data has periodicity
        Args:
            data: single item data with timestamp,
                  like [[1658544527, '100'], [1658544527, '100']...]

        Returns:
            dict: true/false
        """
        data_list = []
        for single_data in data:
            data_list.append(float(single_data[1]))

        fft_series = np.array(data_list)
        fft_periods = self._cal_top_k_period(fft_series)
        max_acf_score, period = self.cal_acf_score(fft_series, fft_periods)
        is_period = True if max_acf_score > self._threshold else False
        ret = {"max_acf_score": str(max_acf_score), "period": int(period), "is_period": is_period}
        return ret
