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
Description: time related utils
"""

import sys
import time
import datetime as dt
from datetime import datetime

from aops_utils.log.log import LOGGER
from aops_utils.validate import validate_time

TIME_FORMAT = '%Y%m%d-%H:%M:%S'


def time_transfer(start_time, end_time):
    """
    Transfer formated time to POSIX timestamp.

    Args:
        start_time (str): start time, set to 0 if None.
        end_time (str): end time, set to current time if None.

    Returns:
        tuple: e.g. (0, 1605077202)
    """
    if start_time is None:
        start_time = 0
    else:
        if '-' not in start_time:
            start_time += '19000101-00:00:00'
        if not validate_time(start_time, TIME_FORMAT):
            LOGGER.error(
                'The start time format is not correct, please refer to %s', TIME_FORMAT)
            sys.exit(0)
        else:
            start_time_struct = datetime.strptime(start_time, TIME_FORMAT)
            # Return integer POSIX timestamp.
            start_time = max(int(start_time_struct.timestamp()), 0)

    now = int(time.time())

    if end_time is None:
        # if end time is not specified, use the current time
        end_time = now
    else:
        if '-' not in end_time:
            end_time += '21001230-23:59:59'
        if not validate_time(end_time, TIME_FORMAT):
            LOGGER.error(
                'The end time format is not correct, please refer to %s', TIME_FORMAT)
            sys.exit(0)
        else:
            end_time_struct = datetime.strptime(end_time, TIME_FORMAT)
            end_time = min(int(end_time_struct.timestamp()), now)

    if start_time > end_time:
        LOGGER.error('The time range is not correct, please check again.')
        sys.exit(0)

    return start_time, end_time


def time_check_generate(starttime, endtime):
    """
    Description: check and generate time

    Args:
        starttime: starttime of the command
        endtime: endtime of the command
    Returns:
        [starttime, endtime]: list of starttime and endtime
    """

    if starttime == "":
        if endtime == "":
            endtime = datetime.now()
            starttime = endtime + dt.timedelta(hours=-1)
        else:
            if not validate_time(endtime, TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s',
                             TIME_FORMAT)
                sys.exit(0)
            starttime = datetime.strptime(endtime, TIME_FORMAT) + dt.timedelta(hours=-1)
    else:
        if endtime == "":
            if not validate_time(starttime, TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s',
                             TIME_FORMAT)
                sys.exit(0)
            endtime = datetime.strptime(starttime, TIME_FORMAT) + dt.timedelta(hours=+1)

    starttime = starttime if isinstance(starttime, str) else starttime.strftime(TIME_FORMAT)
    endtime = endtime if isinstance(endtime, str) else endtime.strftime(TIME_FORMAT)
    starttime, endtime = time_transfer(starttime, endtime)

    return [starttime, endtime]
