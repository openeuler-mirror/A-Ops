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
import uuid
import threading
from flask import jsonify

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import SUCCEED, PARAM_ERROR, TASK_EXECUTION_FAIL
from aops_utils.restful.response import BaseResponse
from aops_utils.database.helper import operate
from aops_manager.conf import configuration
from aops_manager.deploy_manager.run_task import TaskRunner
from aops_manager.account_manager.key import HostKey
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.database.proxy.deploy import DeployProxy
from aops_manager.function.verify.deploy import GenerateTaskSchema, DeleteTaskSchema, \
    GetTaskSchema, ExecuteTaskSchema, ImportTemplateSchema, DeleteTemplateSchema, GetTemplateSchema


class DeleteTask(BaseResponse):
    """
    Interface for delete Task
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete task

        Args:
            task_list(list): task id list
            username(str)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(DeleteTaskSchema,
                                              DeployProxy(configuration),
                                              'delete_task'))


class GenerateTask(BaseResponse):
    """
    Interface for generate Task
    Restful API: post
    """
    @staticmethod
    def _handle(args):
        task_id = str(uuid.uuid1()).replace('-', '')
        args['task_id'] = task_id
        result = {"task_id": task_id}
        status_code = operate(DeployProxy(configuration),
                              args,
                              'add_task')
        return status_code, result

    def post(self):
        """

        Generate task

        Args:
            task_name(str): name of task
            description(str): description of the task
            template_name(list); template name list

        Returns:
            dict: response body

        """
        return jsonify(self.handle_request(GenerateTaskSchema, self))


class GetTask(BaseResponse):
    """
    Interface for get Task
    Restful API: POST
    """

    def post(self):
        """
        Get task

        Args:
            task_list(list): task name list
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(GetTaskSchema,
                                              DeployProxy(configuration),
                                              'get_task'))


class ExecuteTask(BaseResponse):
    """
    Interface for execute Task
    Restful API: post
    """
    @staticmethod
    def _handle(args):
        """
        Handle function

        Args:
            args (dict)

        Returns:
            int: status code
        """
        LOGGER.debug(args)
        task_list = args.get('task_list')
        LOGGER.info("Start run task %s", task_list)

        status_code, response = operate(
            DeployProxy(configuration), args, 'get_task')
        if status_code != SUCCEED:
            return status_code

        inventory = InventoryBuilder()
        for task_info in response['task_infos']:
            task_id = task_info['task_id']
            if not task_info.get('host_list'):
                return PARAM_ERROR
            for host in task_info['host_list']:
                LOGGER.info("Move inventory files from :%s, host name is: %s",
                            configuration.manager.get('HOST_VARS'),
                            host['host_name'])
                inventory.move_host_vars_to_inventory(configuration.manager.get('HOST_VARS'),
                                                      host['host_name'])
            task_thread = threading.Thread(target=ExecuteTask.task_with_remove,
                                           args=(task_id, inventory))
            task_thread.start()
            if task_thread.is_alive():
                return SUCCEED
            LOGGER.error("Task %s execution failed.", task_id)
            return TASK_EXECUTION_FAIL

    def post(self):
        """
        Execute task

        Args:
            task_list(list): task id list

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(ExecuteTaskSchema, self))

    @staticmethod
    def task_with_remove(task_id, inventory):
        """
        Execute task and remove relative files after execution.
        Args:
            inventory(instance): instance of InventoryBuilder
            task_id(str): id of a task.
        """
        res = TaskRunner.run_task(task_id, HostKey.key)
        inventory.remove_host_vars_in_inventory()
        if res:
            LOGGER.info("Task %s execution succeeded.", task_id)
            return
        LOGGER.error("Task %s execution failed.", task_id)


class ImportTemplate(BaseResponse):
    """
    Interface for import template
    Restful API: POST
    """

    def post(self):
        """
        Add template

        Args:
            template_name(str): template name
            template_content(dict): content
            description(str)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(ImportTemplateSchema,
                                              DeployProxy(configuration),
                                              'add_template'))


class GetTemplate(BaseResponse):
    """
    Interface for get template info.
    Restful API: POST
    """

    def post(self):
        """
        Get template info

        Args:
            template_list(list): template id list
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(GetTemplateSchema,
                                              DeployProxy(configuration),
                                              'get_template'))


class DeleteTemplate(BaseResponse):
    """
    Interface for delete template.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete template

        Args:
            template_list(list): template name list

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(DeleteTemplateSchema,
                                              DeployProxy(configuration),
                                              'delete_template'))
