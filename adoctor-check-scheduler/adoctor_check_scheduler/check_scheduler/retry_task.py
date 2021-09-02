#!/usr/bin/python3
# -*- coding:UTF=8 -*-
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
Date: 2021/8/30 15:04
docs: retry_task.py
description: retry task
"""
import time
from adoctor_check_scheduler.common.config import scheduler_check_config


class RetryTask:
    """
    Retry task

    Attributes:
        max_retry_num (int): Maximum number of retries
        cool_down_time (int): Indicates the cooling time of the retry task.
                            This prevents invalid retry due to a short filling interval.
        task_id (int): the task id which marks repeated tasks
        time_range (list): time range of task
        check_item_list (list): check items
        user (str): user of the check task
        host_list (list): host list of the check task
        _enqueue_time (int): Record the time when a task is enqueued.
        _enqueue_count (int): Records the number of times a task is enqueued.
    """
    max_retry_num = scheduler_check_config.check_scheduler.get("MAX_RETRY_NUM")
    cool_down_time = scheduler_check_config.check_scheduler.get("COOL_DOWN_TIME")

    def __init__(self, task_id, time_range, check_item_list, user, host_list):
        """
        Constructor
        Args:
            task_id (int): the task id which marks repeated tasks
            time_range (list): time range of task
            check_item_list (list): check items
            user (str): user of the check task
            host_list (list): host list of the check task
        """
        self.task_id = task_id
        self.time_range = time_range
        self.check_item_list = check_item_list
        self.user = user
        self.host_list = host_list
        self._enqueue_time = -1
        self._enqueue_count = 0

    def is_waiting(self):
        """
        Check whether the task is waiting for cooling.

        Returns:
            True/False
        """
        return int(time.time()) - self._enqueue_time < RetryTask.cool_down_time

    def is_use_up(self):
        """
        Check whether the task cannot be retried,
        that is, the number of retry times exceeds the maximum.

        Returns:
            True/False
        """
        return self._enqueue_count > RetryTask.max_retry_num

    def try_again(self):
        """
        Retry again, number of retries + 1
        """
        self._enqueue_count += 1
        self._enqueue_time = int(time.time())
