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
Description: group  method's entrance for custom commands
Class:HostCommand
"""
import sys
from aops_cli.base_cmd import BaseCommand, str_split, cli_request, add_access_token
from aops_utils.log.log import LOGGER
from aops_utils.restful.helper import make_manager_url
from aops_utils.conf.constant import ADD_GROUP, DELETE_GROUP, GET_GROUP


class GroupCommand(BaseCommand):
    """
    Description: hosts' operations
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='group',
                            help_desc="groups' operations")
        self.sub_parse.add_argument(
            '--action',
            help='group actions: add, delete, query',
            nargs='?',
            type=str,
            required=True,
            choices=['add', 'delete', 'query']
        )

        self.sub_parse.add_argument(
            '--host_group_name',
            help='A group name',
            nargs='?'
        )

        self.sub_parse.add_argument(
            '--host_group_list',
            help='list of group names',
            nargs='?',
            default=""
        )

        self.sub_parse.add_argument(
            '--description',
            help='The description of the host group',
            nargs='?',
            type=str,
            default="This is a host group."
        )

        add_access_token(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        """

        action = params.action

        action_dict = {
            'add': self.manage_requests_add_group,
            'delete': self.manage_requests_delete_group,
            'query': self.manage_requests_query_group
        }

        action_dict.get(action)(params)

    @staticmethod
    def manage_requests_add_group(params):
        """
        Description: Executing add command
        Args:
            params: Command line parameters
        Returns:
            dict: response from the backend
        Raises:

        """

        groups = str_split(params.host_group_name) if params.host_group_name is not None else []
        manager_url, header = make_manager_url(ADD_GROUP)

        if len(groups) != 1:
            LOGGER.error(
                'One group can be added, please try again')
            sys.exit(0)

        pyload = {
            "host_group_name": groups[0],
            "description": params.description,
        }

        return cli_request('POST', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_delete_group(params):
        """
        Description: Executing delete request
        Args:
            params: Command line parameters
        Returns:
            dict: response from the backend
        Raises:
        """

        groups = str_split(params.host_group_list) if params.host_group_list is not None else []
        manager_url, header = make_manager_url(DELETE_GROUP)

        pyload = {
            "host_group_list": groups,
        }

        return cli_request('DELETE', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_query_group(params):
        """
        Description: Executing query request
        Args:
            params: Command line parameters
        Returns:
            dict: response from the backend
        """
        manager_url, header = make_manager_url(GET_GROUP)

        pyload = {
                  }

        return cli_request('GET', manager_url, pyload, header, params.access_token)
