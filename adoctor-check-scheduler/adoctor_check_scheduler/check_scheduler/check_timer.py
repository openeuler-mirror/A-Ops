#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/4 17:20
docs: check_timer.py
description: check timer
"""

import time
from aops_utils.singleton import singleton
from adoctor_check_scheduler.common.config import scheduler_check_config
from adoctor_check_scheduler.common.constant import MIN_TIMESTAMP


@singleton
class CheckTimeKeeper:
    """
    Check Time Keeper

    Attributes:
    _start_time (int): Time when the check scheduler is started
    _last_forward (int): Last Forward Task Time
    _last_backward (int): Last Backward Task Time
    _min_time_stamp (int): Minimum timestamp, end point of backward task
    _backward_task_step (int): Backward Task Interval

    """

    def __init__(self):
        """
        Constructor
        """
        self._start_time = int(time.time())
        self._last_forward = self._start_time
        self._last_backward = self._start_time
        self._min_time_stamp = MIN_TIMESTAMP
        self._backward_task_step = scheduler_check_config.check_scheduler.get("BACKWARD_TASK_STEP")
        self._forward_max_task_step = int(scheduler_check_config.check_scheduler.get(
            "FORWARD_MAX_TASK_STEP"))

    def get_forward_time_range(self):
        """
        Obtains the interval for executing the next forward task.
        Returns:
            time range (list)
        """
        now = int(time.time())
        last = self._last_forward
        if now - last > self._forward_max_task_step:
            now = last + self._forward_max_task_step
        # update last time stamp
        self._last_forward = now
        return [last, now]

    def get_backward_time_range(self):
        """
        Obtains the interval for executing the next backward task.
        Returns:
            time range (list)
        """
        if self._last_backward - self._backward_task_step < self._min_time_stamp:
            return None
        start = self._last_backward - self._backward_task_step
        end = self._last_backward
        self._last_backward = start
        return [start, end]


check_time_keeper = CheckTimeKeeper()
