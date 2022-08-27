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
from typing import Optional
from threading import Lock
from flask import Flask
from aops_check.conf import configuration
from aops_check.database import SESSION
from aops_check.database.dao.workflow_dao import WorkflowDao
from aops_check.core.check.check_scheduler.task_keeper import CheckTaskKeeper
from aops_check.core.check.check_scheduler.time_keeper import time_keeper_manager
from aops_utils.singleton import singleton
from aops_utils.restful.status import SUCCEED, DATABASE_CONNECT_ERROR, PARAM_ERROR
from aops_utils.log.log import LOGGER


@singleton
class CheckScheduler:
    """
    It's a configurable scheduler which needs to configure workflow and app, then start check.
    """

    def __init__(self):
        self._workflow_task_manager = {}
        self._work_flow_list_lock = Lock()
        self.timing_check = True if configuration.check.get("TIMING_CHECK") == "on" else False

    @staticmethod
    def _query_running_workflow() -> tuple:
        """
        Query all running workflow from database

        Returns:
            tuple(int, dict): status, result

        """
        workflow_proxy = WorkflowDao(configuration)
        if not workflow_proxy.connect(SESSION):
            LOGGER.error("Connect to workflow_proxy failed.")
            return DATABASE_CONNECT_ERROR, {}
        status, result = workflow_proxy.get_all_workflow_list("running")
        workflow_proxy.close()
        if status != SUCCEED:
            LOGGER.error("get_workflow_list failed.")
            return status, {}
        return status, result

    def start_all_workflow(self, app: Optional[Flask]) -> int:
        """
        Start all workflow in database
        Args:
            app(Flask): app to add scheduler task

        Returns:
            result(int)

        """
        # Make sure timing check is open
        if not self.timing_check:
            LOGGER.info("Timing check is not turned on.")
            return SUCCEED

        # Query all running workflow from database
        status, result = check_scheduler._query_running_workflow()
        if status != SUCCEED:
            return status

        for workflow_id, workflow_info in result.items():
            step = workflow_info.get("step")
            if step <= 0:
                LOGGER.error("Invalid scheduler timed task step %d", step)
                status = PARAM_ERROR
                continue
            username = workflow_info.get("username")
            self._add_workflow(workflow_id, username, step, app)

        return status

    def _add_workflow(self, workflow_id: str, username: str,
                      step: int, app: Optional[Flask] = None) -> None:
        """
        Add workflow task keeper and timed task
        Args:
            workflow_id(str):  workflow id
            username(str):  user name
            step(int): timed task interval
            app(Flask): app to add scheduler task

        Returns:
            None

        """
        # add time keeper
        time_keeper_manager.add_time_keeper(workflow_id, step)

        # add task keeper and add timed task
        with self._work_flow_list_lock:
            if workflow_id in self._workflow_task_manager:
                check_task_keeper = self._workflow_task_manager[workflow_id]
                check_task_keeper.delete_timed_task(app)
            check_task_keeper = CheckTaskKeeper(workflow_id, username, step)
            check_task_keeper.add_timed_task(app)
            self._workflow_task_manager[workflow_id] = check_task_keeper

    def start_workflow(self, workflow_id: str, username: str, step: int) -> int:
        """
        Start workflow
        Args:
            workflow_id(str):  workflow id
            username(str):  user name
            step(int): timed task interval

        Returns:
            Result(int)

        """
        if not self.timing_check:
            LOGGER.warning("Timing check is not turned on.")
            return SUCCEED

        if step <= 0:
            LOGGER.error("Invalid scheduler timed task step %d", step)
            return PARAM_ERROR
        self._add_workflow(workflow_id, username, step)
        return SUCCEED

    def stop_workflow(self, workflow_id):
        """
        Stop workflow
        Args:
            workflow_id(str):  workflow id

        Returns:
            Result(int)

        """
        if not self.timing_check:
            LOGGER.warning("Timing check is not turned on.")
            return SUCCEED

        # stop timed task and delete task keeper
        with self._work_flow_list_lock:
            if workflow_id not in self._workflow_task_manager:
                LOGGER.warning("workflow_id %s not existed when stop.", workflow_id)
            else:
                check_task_keeper = self._workflow_task_manager[workflow_id]
                check_task_keeper.delete_timed_task()
                self._workflow_task_manager.pop(workflow_id)

        # delete keeper
        time_keeper_manager.delete_time_keeper(workflow_id)
        return SUCCEED


check_scheduler = CheckScheduler()
