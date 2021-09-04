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
Description:
"""

import os
import sys
from datetime import datetime

from aops_utils.log.log import LOGGER


def validate_path(path, file=True):
    """
    judge whether the path is valid.

    Args:
        path (str): path need to be checked.

    Returns:
        bool
    """
    if not os.path.exists(path):
        LOGGER.error("%s does not exist.", path)
        return False

    if not os.access(path, os.R_OK):
        LOGGER.error('Cannot access %s', path)
        return False

    if file and os.path.isdir(path):
        LOGGER.error("Couldn't parse directory %s ", path)
        return False

    return True


def validate_time(time, time_format):
    """
    judge whether the time is matched to format.

    Args:
        time (str): time need to be checked.
        time_format (str): time format.

    Returns:
        bool
    """
    try:
        datetime.strptime(time, time_format)
        return True
    except ValueError as error:
        LOGGER.error(error)
        return False


def name_check(name_list):
    """
    check name with ','
    Args:
        name_list(list): list of name
    """
    for item in name_list:
        if item == "" or item.isspace():
            print("Null string, space string and name ends with ',' are not accepted.")
            print("please check your input.")
            sys.exit(0)


def str_split(string):
    """
    Description: split str args into list
    Args:
        string(str): The string need to be splited.
    Returns:
        list of items
    """
    if string:
        return string.split(",")
    return []
