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
Date: 2022/8/26
docs: task_keeper.py
description: Check scheduler task manager
"""
from typing import Optional
from flask import Flask, current_app
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER
from aops_check.conf import configuration
from aops_check.core.check.check_scheduler.time_keeper import time_keeper_manager


class CheckTaskKeeper:
    """
    Check task keeper
    """

    def __init__(self, workflow_id: str, username: str, step: int):
        """
        Constructor
        """
        self._step = step if step else 60
        self._workflow_id = workflow_id
        self._username = username

    @staticmethod
    def create_task(workflow_id: str, username: str) -> bool:
        """
        Create single check task
        Args:
            workflow_id (str): workflow id
            username (str): user name of workflow

        Returns:
            result (bool): create result

        """
        # Get time range
        time_range = time_keeper_manager.get_time_range(workflow_id)
        if not time_range:
            LOGGER.error("Failed to get time range of %s ", workflow_id)
            return False

        check_msg = {"workflow_id": workflow_id,
                     "username": username,
                     "time_range": time_range}
        return CheckTaskKeeper.publish_check_task(check_msg)

    @staticmethod
    def publish_check_task(task_msg: dict) -> bool:
        """
        Publish check task to kafka
        Args:
            task_msg (dict): task msg

        Returns:
            result (bool): publish result
        """
        try:
            producer = BaseProducer(configuration)
            LOGGER.debug("Send check task msg %s", task_msg)
            producer.send_msg(configuration.producer.get('TASK_NAME'), task_msg)
            return True
        except ProducerInitError as exp:
            LOGGER.error("Produce task msg failed. ", exp)
            return False

    def add_timed_task(self, app: Optional[Flask] = None) -> None:
        """
        Add timed check tasks
        Args:
            app: Flask application of check

        Returns:
            None

        """
        # Creating a Forward Scheduled Task
        job_def = {'id': self._workflow_id,
                   'func': CheckTaskKeeper.create_task,
                   'trigger': 'interval',
                   'seconds': self._step,
                   'args': [self._workflow_id, self._username],
                   'max_instances': 10}
        # If an app is specified, use this app.
        # Otherwise, use current_app
        if app:
            app.apscheduler.scheduler.add_job(**job_def)
            return
        current_app.apscheduler.scheduler.add_job(**job_def)

    def delete_timed_task(self, app: Optional[Flask] = None) -> None:
        """
        Delete timed check tasks
        Args:
            app: Flask application of check

        Returns:
            None

        """
        # If an app is specified, use this app.
        # Otherwise, use current_app
        if app:
            app.apscheduler.scheduler.remove_job(self._workflow_id)
            return
        current_app.apscheduler.remove_job(self._workflow_id)
