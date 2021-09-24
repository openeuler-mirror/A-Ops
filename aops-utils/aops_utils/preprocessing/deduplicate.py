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
Date: 2021/9/24 09:20
docs: deduplicate.py
description: deduplicate the data vector
"""


def deduplicate_certain_data(data_list):
    """
    Data with the same timestamp is combined and deduplicated.

    Args:
        data_list(list): the all original data, e.g.
        "data1": [[1,"str1"], [2,"str2"], [3,"str3"]]

    Returns:
        list: deduplicated data
    """
    if not data_list:
        return data_list
    ret_data_list = []
    cur_data_item = data_list[0]
    for i in range(1, len(data_list)):
        if data_list[i][0] == cur_data_item[0]:
            cur_data_item[1] = "{} {}".format(cur_data_item[1], data_list[i][1])
        else:
            ret_data_list.append(cur_data_item)
            cur_data_item = data_list[i]
    ret_data_list.append(cur_data_item)
    return ret_data_list


def deduplicate(data_vector):
    """
    Data with the same timestamp is combined and deduplicated.

    Args:
        data_vector(dict): the all original data, e.g. {
            "data1": [[1,"str1"], [2,"str2"], [3,"str3"]],
            "data2": [[1,"str1"], [2,"str2"],]
        }

    Returns:
        dict: deduplicated data
    """
    result = {}
    for key, column in data_vector.items():
        column_res = deduplicate_certain_data(column)
        result[key] = column_res

    return result
