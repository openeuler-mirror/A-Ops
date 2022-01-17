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
from flask import request
from flask import jsonify,json

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import StatusCode, SUCCEED, PARAM_ERROR, TASK_EXECUTION_FAIL
from aops_manager.conf import configuration
from aops_manager.deploy_manager.run_task import TaskRunner
from aops_manager.account_manager.key import HostKey
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_utils.restful.resource import BaseResource
from aops_manager.deploy_manager.database.deploy import DeployDatabase
from aops_manager.function.verify.deploy import GenerateTaskSchema, DeleteTaskSchema, \
    GetTaskSchema, ExecuteTaskSchema, ImportTemplateSchema, DeleteTemplateSchema, GetTemplateSchema


class DeleteTask(BaseResource):
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
        return self.restful_result('delete_task', DeployDatabase(), DeleteTaskSchema)


class GenerateTask(BaseResource):
    """
    Interface for generate Task
    Restful API: post
    """

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
        # generate task id
        args = self.request_data(request)
        task_id = str(uuid.uuid1()).replace('-', '')
        payload = {
            'task_id': task_id,
        }
        args.update(payload)

        return self.restful_result("add_task", DeployDatabase(), GenerateTaskSchema, args=args)


class GetTask(BaseResource):
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
        return self.restful_result("get_task", DeployDatabase(), GetTaskSchema)


class ExecuteTask(BaseResource):
    """
    Interface for execute Task
    Restful API: post
    """

    def post(self):
        """
        Execute task

        Args:
            task_list(list): task id list

        Returns:
            dict: response body
        """
        args = self.request_data(request)
        inventory = InventoryBuilder()
        LOGGER.debug(args)
        task_list = args.get('task_list')
        LOGGER.info("Start run task %s", task_list)
        response = json.loads(self.restful_result("get_task", DeployDatabase(), ExecuteTaskSchema))
        if response['code'] != SUCCEED:
            return jsonify(response)
        for task_info in response['task_infos']:
            task_id = task_info['task_id']
            if not task_info.get('host_list'):
                return StatusCode.make_response(PARAM_ERROR)
            for host in task_info['host_list']:
                LOGGER.info("Move inventory files from :%s, host name is: %s", configuration.manager.get('HOST_VARS'),
                            host['host_name'])
                inventory.move_host_vars_to_inventory(configuration.manager.get('HOST_VARS'),
                                                      host['host_name'])
            task_thread = threading.Thread(target=ExecuteTask.task_with_remove,
                                           args=(task_id, inventory))
            task_thread.start()
            if task_thread.is_alive():
                response = StatusCode.make_response(SUCCEED)
                return jsonify(response)
            response = StatusCode.make_response(TASK_EXECUTION_FAIL)
            LOGGER.error("Task %s execution failed.", task_id)
            return jsonify(response)

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


class ImportTemplate(BaseResource):
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
        return self.restful_result('add_template', DeployDatabase(), ImportTemplateSchema)


class GetTemplate(BaseResource):
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
        return self.restful_result('get_template', DeployDatabase(), GetTemplateSchema)


class DeleteTemplate(BaseResource):
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
        return self.restful_result('delete_template', DeployDatabase(), DeleteTemplateSchema)
