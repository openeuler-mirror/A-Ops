#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description: Alignment algorithm
"""
import bisect


def get_primary_data(data):
    """
    Get the anchor of multiple data series according to data length

    Args:
        data(dict): e.g. {
            "data1": [[1,2]],
            "data2": [[2,3], [4,5]]
        }

    Returns:
        str: key of the anchor data
    """
    res = sorted(data, key = lambda k: len(data[k]))
    return res[0]


def make_time_series(period, time_range, data):
    """
    Create a time series with periodic intervals

    Args:
        period(int): sampling period
        time_range(list): time range
        data(list): data series

    Returns:
        list: time series
    """
    cur_time = data[0][0]
    time_series = []

    while cur_time < time_range[1]:
        time_series.append(cur_time)
        cur_time += period
        if cur_time > data[-1][0]:
            break

    return time_series


def handle_right_boundary(time_index, time_series, column, column_res):
    """
    In case that there is missing data in the right boundary of current time

    Args:
        time_index(int): index of the current time in time series
        time_series(list): time series
        column(list): original data
        column_res(list): aligned data
    """
    time_len = len(time_series)
    while time_index < time_len:
        cur_value = column[-1][1]
        column_res.append([time_series[time_index], cur_value])
        time_index += 1


def get_cur_value(pos, column, cur_time):
    """
    Get the most closest adjusted value based on the current time

    Args:
        pos(int): position obtained by bisect
        column(list): original data
        cur_time(int): current time

    Returns:
        int: value
    """
    if pos == 0:
        cur_value = column[pos][1]
    elif column[pos - 1][0] + column[pos][0] > 2 * cur_time:
        cur_value = column[pos - 1][1]
    else:
        cur_value = column[pos][1]

    return cur_value


def align_certain_data(time_series, column):
    """
    Align data

    Args:
        time_series(list): time series
        column(list): original data

    Returns:
        list: aligned data
    """
    column_time = [item[0] for item in column]
    column_len = len(column)
    column_res = []
    for time_index, cur_time in enumerate(time_series):
        pos = bisect.bisect_left(column_time, cur_time)
        if pos >= column_len:
            handle_right_boundary(time_index, time_series, column, column_res)
            break
        cur_value = get_cur_value(pos, column, cur_time)
        column_res.append([cur_time, cur_value])

    return column_res


def align(period, time_range, data):
    """
    Align the whole data

    Args:
        period(int): sampling period
        time_range(list): time range
        data(dict): the all original data, e.g. {
            "data1": [[1,2]],
            "data2": [[2,3], [4,5]]
        }

    Returns:
        dict: aligned data
    """
    result = {}
    primary = get_primary_data(data)
    if len(data[primary]) == 0:
        return result

    time_series = make_time_series(period, time_range, data[primary])

    for key, column in data.items():
        column_res = align_certain_data(time_series, column)
        result[key] = column_res

    return result
