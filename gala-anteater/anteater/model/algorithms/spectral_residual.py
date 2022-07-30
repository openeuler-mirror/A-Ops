#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
Description: The implementation of spectral residual anomaly detection, please refer to the link:
             - https://github.com/microsoft/anomalydetector.
             - https://arxiv.org/pdf/1906.03821.pdf.
"""

import math
import numpy as np

from anteater.utils.log import Log

log = Log().get_logger()


def series_filter(values, kernel_size: int):
    """Filtering the time series values"""
    result = np.cumsum(values, dtype=np.float32)

    result[kernel_size:] = result[kernel_size:] - result[:-kernel_size]

    if kernel_size <= 0:
        raise ValueError("The kernal size less than or equal to zero.")

    result[kernel_size:] = np.divide(result[kernel_size:], kernel_size)

    for i in range(1, kernel_size):
        result[i] /= i + 1

    return result


def extrapolate_next(values):
    """Extrapolates the next value by sum up the slope of
    the last value with previous values
    """
    last_val = values[-1]

    slope = [0]
    for i, val in enumerate(values[::-1]):
        if i == 0:
            continue
        else:
            tmp_value = np.divide((last_val - val), i)
            slope.append(tmp_value)

    next_vals = last_val + np.cumsum(slope)

    return next_vals


def merge_series(values, extend_num: int, forward: int):
    """Merges the series of values"""
    next_value = extrapolate_next(values)[forward]
    extension = [next_value] * extend_num

    if isinstance(values, list):
        merged_vales = values + extension
    else:
        merged_vales = np.append(values, extension)

    return merged_vales


class SpectralResidual:
    """The implementation of spectral residual anomaly detection"""

    def __init__(self, amp_size: int, series_size: int, score_size: int) -> None:
        """The spectral residual initializer"""
        self.amp_size = amp_size
        self.series_size = series_size
        self.score_size = score_size

    def amplitude(self, values):
        """Transforms the time-series into sliency map"""
        freq = np.fft.fft(values)
        magn = np.sqrt(freq.real ** 2 + freq.imag ** 2)
        sr = np.exp(np.log(magn) - series_filter(np.log(magn), self.amp_size))

        freq.real = np.divide(freq.real * sr, magn)
        freq.imag = np.divide(freq.imag * sr, magn)

        s_amp = np.fft.ifft(freq)
        return s_amp

    def compute_score(self, values):
        """Computes **average** anomaly score by spectral residual"""
        merged_vales = merge_series(values, self.series_size, self.series_size)

        amp = self.amplitude(merged_vales)
        sr = np.sqrt(amp.real ** 2 + amp.imag ** 2)
        sr = sr[: len(values)]

        filtered_val = series_filter(sr, self.score_size)
        score = np.divide((sr - filtered_val), filtered_val)

        return score
