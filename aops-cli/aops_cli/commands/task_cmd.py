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
Description: task  method's entrance for custom commands
Class:TaskCommand
"""

from aops_cli.base_cmd import BaseCommand, cli_request, add_access_token, add_query_args
from aops_utils.validate import name_check, str_split
from aops_utils.conf.constant import GENERATE_TASK, DELETE_TASK, GET_TASK, EXECUTE_TASK
from aops_utils.restful.helper import make_manager_url
from aops_utils.cli_utils import add_page

class TaskCommand(BaseCommand):
    """
    Description: task' operations
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='task',
                            help_desc="tasks' operations")
        self.sub_parse.add_argument(
            '--action',
            help='task actions: generate, execute, delete, query',
            nargs='?',
            type=str,
            required=True,
            choices=['generate', 'execute', 'delete', 'query'])

        self.sub_parse.add_argument(
            '--task_name',
            help='task name',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--task_list',
            help='list of task ids',
            nargs="?",
            type=str,
            default=""
        )

        self.sub_parse.add_argument(
            '--template_name',
            help='template list will be used by the task',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--description',
            help='task description',
            nargs='?',
            type=str,
            default="The task's description is null")

        add_access_token(self.sub_parse)
        add_query_args(self.sub_parse, ['task_name'])
        add_page(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:
            dict: response of the backend
        """

        action = params.action

        action_dict = {
            'generate': self.manage_requests_generate_task,
            'execute': self.manage_requests_query_delete_execute,
            'delete': self.manage_requests_query_delete_execute,
            'query': self.manage_requests_query_delete_execute
        }
        kwargs = {
            "action": action,
            "params": params

        }
        action_dict.get(action)(**kwargs)

    @staticmethod
    def manage_requests_generate_task(**kwargs):
        """
        Description: Executing generate command
        Args:
            params: Command line parameters
            action: task action
        Returns:
            dict: response of the backend
        Raises:
        """
        params = kwargs.get('params')
        task_name = str_split(params.task_name)
        templates = str_split(params.template_name)
        name_check(task_name)
        name_check(templates)
        manager_url, header = make_manager_url(GENERATE_TASK)

        pyload = {
            "task_name": task_name[0],
            "description": params.description,
            "template_name": templates,
        }
        return cli_request('POST', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_query_delete_execute(**kwargs):
        """
        Description: Executing query or delete or excute request
        Args:
            params: Command line parameters
            action: task action
        Returns:
            dict: response of the backend
        Raises:
        """
        params = kwargs.get('params')
        action = kwargs.get('action')
        task_ids = str_split(params.task_list) if params.task_list is not None else []
        name_check(task_ids)
        url_dict = {
            'execute': [make_manager_url(EXECUTE_TASK), 'POST'],
            'delete': [make_manager_url(DELETE_TASK), 'DELETE'],
            'query': [make_manager_url(GET_TASK), 'POST']
        }

        manager_url, header = url_dict.get(action)[0]
        url_operation = url_dict.get(action)[1]
        if url_operation == 'DELETE' and len(task_ids) == 0:
            print("No task will be deleted, because of the empty task list.")
            print("Please check your task list if you want to delete tasks.")

        pyload = {
            "task_list": task_ids,
        }
        if action == 'query':
            pyload['page'] = params.page
            pyload['per_page'] = params.per_page
        return cli_request(url_operation, manager_url, pyload, header, params.access_token)
