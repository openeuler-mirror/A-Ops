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
Time: 2022-08-26
Author: YangYunYi
Description: Time keeper of check scheduler
"""

import time
from typing import List
from threading import Lock
from aops_utils.singleton import singleton
from aops_utils.log.log import LOGGER


class CheckTimeKeeper:
    """
    Check Time Keeper
    """

    def __init__(self, step: int):
        """
        Constructor
        """
        self._step = step if step else 60
        self._last_moment = int(time.time())

    def get_time_range(self) -> List[int]:
        """
        Obtains the interval for executing the next forward task.
        Returns:
            time range (list)
        """
        now = int(time.time())
        last = self._last_moment
        if now - last > self._step:
            now = last + self._step
        # update last time stamp
        self._last_moment = now
        return [last, now]


@singleton
class TimeKeeperManager:
    """
    Check Time Keeper manager
    """

    def __init__(self):
        """
        Constructor
        """
        self._cache = {}
        self._time_keeper_lock = Lock()

    def add_time_keeper(self, workflow_id: str, step: int) -> None:
        """
        Add a new time keeper
        Args:
            workflow_id (str): workflow id of the time keeper
            step (int): step of timer

        Returns:
            None
        """
        with self._time_keeper_lock:
            if workflow_id in self._cache:
                LOGGER.warning("The time keeper of workflow %s is "
                               "existed. Update a new one.", workflow_id)
                self._cache.pop(workflow_id)
            self._cache[workflow_id] = CheckTimeKeeper(step)

    def delete_time_keeper(self, workflow_id) -> None:
        """
        Add a new time keeper
        Args:
            workflow_id (str): workflow id of the time keeper

        Returns:
            None
        """
        with self._time_keeper_lock:
            if workflow_id not in self._cache:
                LOGGER.warning("The time keeper of workflow %s is "
                               "not existed. Delete nothing.", workflow_id)
                return
            self._cache.pop(workflow_id)

    def get_time_range(self, workflow_id) -> List[int]:
        """
        Get time range of a workflow timer
        Args:
            workflow_id (str): workflow id of the time keeper

        Returns:
            time_range(list)
        """
        with self._time_keeper_lock:
            if workflow_id in self._cache:
                return self._cache[workflow_id].get_time_range()
            LOGGER.warning("Cannot find the  time keeper of workflow %s "
                           "when get time range.", workflow_id)
            return []


time_keeper_manager = TimeKeeperManager()
