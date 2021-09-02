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
Author: YangYunYi
Date: 2021/8/5 15:17
docs: parser.py
description: built-in function of expression check rule
"""
import operator
from adoctor_check_executor.common.check_error import ExpressionFunctionError


def get_operator_function(op_sign):
    """
    Get operator function from sign
    Args:
        op_sign (str): operator sign

    Returns:
        operator function
    """
    return {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
    }[op_sign]


def builtin_count(target, args_list, data_backpack):
    """
    Built-in function of Count
    Args:
        target (str): target data name
        args_list(list): argument list [time_shift, data_item, operator]
        data_backpack (DataBackpack): data cache

    Returns:
        count result (int)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 3:
        raise ExpressionFunctionError("Invalid num of arguments, %s" % args_list)

    time_shift = args_list[0].calculate(data_backpack)
    data_pattern = args_list[1].calculate(data_backpack)
    judge_op = args_list[2].calculate(data_backpack)

    data_name = data_backpack.get_key_data_name(target)

    try:
        ret = 0
        cur_time_stamp = data_backpack.get_time_stamp(data_backpack.target_index, data_name)
        shift_time_stamp = cur_time_stamp - time_shift
        index = data_backpack.target_index
        while index >= 0:
            if data_backpack.get_time_stamp(index, data_name) < shift_time_stamp:
                break
            if get_operator_function(judge_op)(
                    data_backpack.get_data_value(index, data_name),
                    data_pattern):
                ret += 1
            index -= 1
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp
    return ret


def builtin_max(target, args_list, data_backpack):
    """
    Built-in function of Max
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        max result (int)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    time_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    ret = float('-inf')

    try:
        cur_time_stamp = data_backpack.get_time_stamp(data_backpack.target_index, data_name)
        shift_time_stamp = cur_time_stamp - time_shift
        index = data_backpack.target_index
        while index >= 0:
            if data_backpack.get_time_stamp(index, data_name) < shift_time_stamp:
                break
            ret = max(data_backpack.get_data_value(index, data_name), ret)
            index -= 1
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp
    return ret


def builtin_min(target, args_list, data_backpack):
    """
    Built-in function of min
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        max result (int)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    time_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    ret = float('inf')

    try:
        cur_time_stamp = data_backpack.get_time_stamp(data_backpack.target_index, data_name)
        shift_time_stamp = cur_time_stamp - time_shift
        index = data_backpack.target_index
        while index >= 0:
            if data_backpack.get_time_stamp(index, data_name) < shift_time_stamp:
                break
            ret = min(data_backpack.get_data_value(index, data_name), ret)
            index -= 1
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp
    return ret


def builtin_sum(target, args_list, data_backpack):
    """
    Built-in function of sum
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        max result (int)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    time_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    ret = 0

    try:
        cur_time_stamp = data_backpack.get_time_stamp(data_backpack.target_index, data_name)
        shift_time_stamp = cur_time_stamp - time_shift
        index = data_backpack.target_index
        while index >= 0:
            if data_backpack.get_time_stamp(index, data_name) < shift_time_stamp:
                break
            ret += data_backpack.get_data_value(index, data_name)
            index -= 1
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp
    return ret


def builtin_avg(target, args_list, data_backpack):
    """
    Built-in function of average
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        max result (int)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    time_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    sum_value = 0

    try:
        cur_time_stamp = data_backpack.get_time_stamp(data_backpack.target_index, data_name)
        shift_time_stamp = cur_time_stamp - time_shift
        index = data_backpack.target_index
        count = index
        while index >= 0:
            if data_backpack.get_time_stamp(index, data_name) < shift_time_stamp:
                break
            sum_value += data_backpack.get_data_value(index, data_name)
            index -= 1
        ret = sum_value / count
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp
    return ret


def builtin_keyword(target, args_list, data_backpack):
    """
    Built-in function of Keyword
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        Keyword result (bool)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    keyword = args_list[0].calculate(data_backpack)

    data_name = data_backpack.get_key_data_name(target)
    try:
        data_value = data_backpack.get_data_value(data_backpack.target_index, data_name)

    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp

    if data_value.find(keyword) != -1:
        return True
    return False


def builtin_diff(target, args_list, data_backpack):
    """
    Built-in function of Diff
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        Diff result (bool)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    num_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    if data_backpack.target_index == 0:
        raise ExpressionFunctionError("Invalid index is 0")
    try:
        data_value = data_backpack.get_data_value(data_backpack.target_index, data_name)
        pre_data_value = data_backpack.get_data_value(
            data_backpack.target_index - num_shift,
            data_name)
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp

    return data_value != pre_data_value


def builtin_abschange(target, args_list, data_backpack):
    """
    Built-in function of abschange
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        Diff result (bool)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    num_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    if data_backpack.target_index == 0:
        raise ExpressionFunctionError("Invalid index is 0")
    try:
        data_value = data_backpack.get_data_value(data_backpack.target_index, data_name)
        pre_data_value = data_backpack.get_data_value(
            data_backpack.target_index - num_shift,
            data_name)
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp

    return abs(data_value - pre_data_value)


def builtin_change(target, args_list, data_backpack):
    """
    Built-in function of abschange
    Args:
        target (str): target data name
        args_list(list): argument list
        data_backpack (DataBackpack): data cache

    Returns:
        Diff result (bool)

    Raise:
        ExpressionFunctionError
    """
    if len(args_list) != 1:
        raise ExpressionFunctionError("Invalid num of arguments")

    num_shift = args_list[0].calculate(data_backpack)
    data_name = data_backpack.get_key_data_name(target)
    if data_backpack.target_index == 0:
        raise ExpressionFunctionError("Invalid index is 0")
    try:
        data_value = data_backpack.get_data_value(data_backpack.target_index, data_name)
        pre_data_value = data_backpack.get_data_value(
            data_backpack.target_index - num_shift,
            data_name)
    except ExpressionFunctionError as exp:
        raise ExpressionFunctionError("calculate failed, %s" % exp) from exp

    return data_value - pre_data_value
