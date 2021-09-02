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
Date: 2021/8/4 15:39
docs: task_manager.py
description: Check task manager
"""
import time
import queue
from adoctor_check_scheduler.check_scheduler.retry_task import RetryTask
from adoctor_check_scheduler.check_scheduler.check_timer import check_time_keeper
from adoctor_check_scheduler.common.config import scheduler_check_config
from adoctor_check_scheduler.common.constant import CheckTopic, FORWARD_TASK_ID, BACKWARD_TASK_ID
from aops_utils.singleton import singleton
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER
from aops_utils.conf.constant import DATA_GET_HOST_INFO_BY_USER
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_datacenter_url
from aops_utils.restful.status import SUCCEED


@singleton
class CheckTaskManager:
    """
    Check task manager

    Attributes:
        max_dead_retry_task_num (int): Maximum number of dead retry tasks recorded in the memory
        _retry_queue (Queue): Retry task queue
        _retry_id_list (dict): Record the mapping between the ID of the retry task
                                and the task object. The dead task will be deleted and
                                the dead retry task will be added.
        _dead_retry_task (list): Record the IDs of dead tasks to check whether the tasks are dead.
                                If the number of dead tasks exceeds a certain value,
                                the list will be cleared.
    """
    max_dead_retry_task_num = scheduler_check_config.check_scheduler.get("MAX_DEAD_RETRY_TASK")

    def __init__(self):
        """
        Constructor
        """
        self._retry_queue = queue.Queue()
        self._retry_id_list = dict()
        self._dead_retry_task = []

    def create_retry_task(self, task_id, time_range, check_item_list, user, host_list):
        """
        Creating a Retry Task
        Args:
            task_id (int): the task id which marks repeated tasks
            time_range (list): time range of task
            check_item_list (list): check items
            user (str): user of the check task
            host_list (list): host list of the check task
        """
        # The task already exists.
        if task_id in self._retry_id_list.keys():
            return self._retry_id_list.get(task_id)

        # Tasks that do not need to be retried
        if task_id in self._dead_retry_task:
            LOGGER.info("This task %d is dead.", task_id)
            return None

        # Obtains the 13-bit timestamp as the task ID.
        task_id = int(round(time.time() * 1000))
        retry_task = RetryTask(task_id, time_range, check_item_list, user, host_list)
        self._retry_id_list[task_id] = retry_task
        return retry_task

    def _add_dead_retry_task(self, task_id):
        """
        Adding a Dead Retry Task
        Args:
            task_id (int): task id
        """
        self._dead_retry_task.append(task_id)
        if len(self._dead_retry_task) > check_task_manager.max_dead_retry_task_num:
            target_size = CheckTaskManager.max_dead_retry_task_num * \
                          scheduler_check_config.check_scheduler.get("DEAD_RETRY_TASK_DISCOUNT")
            del self._dead_retry_task[0: target_size]
            LOGGER.debug("Cut dead_retry_task to size: %d", target_size)

    def enqueue_retry_task(self, retry_task):
        """
        Add retry task to retry queue
        Args:
            retry_task (RetryTask): retry task need retry
        """
        # The number of task retries exceeds the maximum.
        if not retry_task.is_use_up():
            retry_task.try_again()
            self._retry_queue.put(retry_task)
        else:
            self._add_dead_retry_task(retry_task.task_id)
            self._retry_id_list.pop(retry_task.task_id)
        self.print_retry_queue_status()

    def dequeue_retry_task(self):
        """
        Retrieve the retry task.
        Returns:
            retry_task (RetryTask/None)
        """
        task_num = self._retry_queue.qsize()
        while task_num > 0:
            retry_task = self._retry_queue.get()
            if retry_task.is_waiting():
                self._retry_queue.put(retry_task)
            else:
                self.print_retry_queue_status()
                return retry_task
            task_num -= 1
        LOGGER.debug("Get no task")
        return None

    def print_retry_queue_status(self):
        """
        Print the status of the retry queue
        """
        LOGGER.debug("Retry queue size: %s, retry_id_list size %s, dead_retry_task size %s ",
                     self._retry_queue.qsize(),
                     len(self._retry_id_list),
                     len(self._dead_retry_task))

    @staticmethod
    def create_task_msg(time_range, check_item_list, user, host_list, task_id=0):
        """
        Create Task Message
        Args:
            time_range (list): time range of task
            check_item_list (list) check item list
            user (str): user of check task
            host_list (list): host list
            task_id (int): Indicates the retry task. For other tasks, the value is 0.

        Returns:
            msg (dict)
        """
        msg = {"task_id": task_id,
               "user": user,
               "host_list": host_list,
               "check_items": check_item_list,
               "time_range": time_range}
        return msg

    @staticmethod
    def get_host_list():
        """
        Get host list from Data base
        """
        # Forward to database
        msg = {
            "username": []
        }
        database_url = make_datacenter_url(DATA_GET_HOST_INFO_BY_USER)
        response = MyResponse.get_result(
            SUCCEED, 'post', database_url, msg)
        if response.get("code") != SUCCEED:
            LOGGER.error("Get host_list failed")
            return None
        host_infos = response.get("host_infos")
        if not host_infos:
            LOGGER.error("No host_infos found in response")
            return None

        # Delete irrelevant information.
        new_host_info = dict()
        for user, host_list in host_infos.items():
            new_host_list = []
            for host in host_list:
                if "host_id" not in host.keys() or "public_ip" not in host.keys():
                    continue
                new_host = dict()
                new_host["host_id"] = host.get("host_id")
                new_host["public_ip"] = host.get("public_ip")
                new_host_list.append(new_host)
            if new_host_list:
                new_host_info[user] = new_host_list
        return new_host_info

    @staticmethod
    def create_forward_task():
        """
        Perform regular check tasksa
        Returns:
            None

        """
        # Get time range
        time_range = check_time_keeper.get_forward_time_range()
        # Get host list
        host_list_info = check_task_manager.get_host_list()
        if not host_list_info:
            LOGGER.warning("No host found in time range %s", time_range)
            return

        for user, host_list in host_list_info.items():
            check_msg = check_task_manager.create_task_msg(time_range, [],
                                                           user, host_list,
                                                           FORWARD_TASK_ID)
            check_task_manager.publish_check_task(check_msg)
        return

    @staticmethod
    def create_backward_task():
        """
        Perform regular check tasks
        Returns:
            None

        """

        # Preferentially execute tasks that need to be retried.
        retry_task = check_task_manager.dequeue_retry_task()
        if retry_task is not None:
            check_msg = check_task_manager.create_task_msg(retry_task.time_range,
                                                           retry_task.check_item_list,
                                                           retry_task.user,
                                                           retry_task.host_list,
                                                           retry_task.task_id)
            check_task_manager.publish_check_task(check_msg)
            return

        # Creating a Backtracking Task
        time_range = check_time_keeper.get_backward_time_range()
        if time_range is None:
            LOGGER.error("time_range is none, Maybe the bakward task has completed")
            return

        host_list_info = check_task_manager.get_host_list()
        if not host_list_info:
            LOGGER.warning("No host found in time_range %s.", time_range)
            return

        for user, host_list in host_list_info.items():
            check_msg = check_task_manager.create_task_msg(time_range, [],
                                                           user, host_list,
                                                           BACKWARD_TASK_ID)
            check_task_manager.publish_check_task(check_msg)

        return

    @staticmethod
    def publish_check_task(task_msg):
        """
        Publish check task
        Args:
            task_msg (dict): task msg
        """
        try:
            producer = BaseProducer(scheduler_check_config)
            LOGGER.debug("Send check task msg %s", task_msg)
            producer.send_msg(CheckTopic.do_check_topic, task_msg)
        except ProducerInitError as exp:
            LOGGER.error("Produce task msg failed. %s" % exp)

    @staticmethod
    def add_timed_task(app):
        """
        Timed check tasks
        Args:
            app: application of check

        Returns:
            None

        """
        # Creating a Forward Scheduled Task
        app.apscheduler.add_job(func=check_task_manager.create_forward_task,
                                id='forward_check',
                                trigger='interval',
                                seconds=scheduler_check_config.check_scheduler.get(
                                    "FORWARD_TASK_INTERVAL"))

        # Creating a Backward Scheduled Task
        app.apscheduler.add_job(func=check_task_manager.create_backward_task,
                                id='backward_check',
                                trigger='interval',
                                seconds=scheduler_check_config.check_scheduler.get(
                                    "BACKWARD_TASK_INTERVAL"))


check_task_manager = CheckTaskManager()
