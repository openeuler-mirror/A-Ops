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
Description: hosts method's entrance for custom commands
Class:HostCommand
"""
import sys

from aops_cli.base_cmd import BaseCommand
from aops_utils.validate import name_check, str_split
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_manager_url
from aops_utils.conf.constant import ADD_HOST, DELETE_HOST, QUERY_HOST, QUERY_HOST_DETAIL
from aops_utils.restful.status import SUCCEED
from aops_utils.cli_utils import add_page, cli_request, add_access_token, add_query_args
from aops_utils.cli_utils import print_row_from_result


class HostCommand(BaseCommand):
    """
    Description: hosts' operations
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='host',
                            help_desc="hosts' operations")
        self.sub_parse.add_argument(
            '--action',
            help='host actions: add, delete, query',
            nargs='?',
            type=str,
            required=True,
            choices=['add', 'delete', 'query'])

        self.sub_parse.add_argument(
            '--host_name',
            help='name of the host will be added',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--host_list',
            help='host list',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--host_group_name',
            help='group names',
            nargs='?',
            default="")

        self.sub_parse.add_argument(
            '--management',
            help='show whether the host added or queried '
                 'is management node, default is False: monitor.',
            nargs='?',
            type=str,
            default="",
            choices=['True', 'False']
        )

        self.sub_parse.add_argument(
            '--public_ip',
            help='public ip address be added',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--verbose',
            help='verbose to show details of the host',
            nargs='?',
            type=str,
            default="False",
            choices=['True', 'False']
        )

        self.sub_parse.add_argument(
            '--ssh_port',
            help='host\'s ssh port, default is 22',
            type=int,
            default=22)

        self.sub_parse.add_argument(
            '--username',
            nargs='?',
            help='The user account',
            type=str
        )

        self.sub_parse.add_argument(
            '--password',
            nargs='?',
            help='The password of user account',
            type=str
        )

        self.sub_parse.add_argument(
            '--sudo_password',
            help='The sudo password of the host will be added',
            nargs='?',
            type=str
        )

        self.sub_parse.add_argument(
            '--key',
            help='The key to crypt.',
            nargs='?',
            type=str
        )

        add_access_token(self.sub_parse)
        add_query_args(self.sub_parse, ['host_name', 'host_group_name'])
        add_page(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params(argparse.Namespace): Command line parameters
        """

        action = params.action
        action_dict = {
            'add': self.manage_requests_add,
            'delete': self.manage_requests_delete,
            'query': self.manage_requests_query
        }
        return action_dict.get(action)(params)

    @staticmethod
    def manage_requests_add(params):
        """
        Description: Executing add command
        Args:
            params{dict}: Command line parameters
        Returns:
            dict: response of the backend
        """

        manager_url, header = make_manager_url(ADD_HOST)
        management = True if params.management == "True" else False
        host_name = str_split(params.host_name)
        if len(host_name) != 1:
            print("Invalid host name or more than one host is added.")
            print("',' cannot be contained in host_name, please try again.")
            sys.exit(0)
        name_check(host_name)
        if params.management is None:
            params.management = False
        pyload = {
            "key": params.key,
            "host_list": [
                {
                    "host_name": host_name[0],
                    "host_group_name": params.host_group_name,
                    "public_ip": params.public_ip,
                    "ssh_port": params.ssh_port,
                    "management": management,
                    "username": params.username,
                    "password": params.password,
                    "sudo_password": params.sudo_password
                }
            ]
        }

        return cli_request('POST', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_query(params):
        """
        Description: Executing query request
        Args:
            params: Command line parameters
        Returns:
            dict: response of the backend
        """
        if params.host_group_name is None:
            print("Host_group_name cannot be none, please input valid host_group_name")
            sys.exit(0)
        if params.management is None:
            print("Management cannot be none, please input valid management")
            sys.exit(0)
        groups = str_split(params.host_group_name)
        name_check(groups)
        pyload = {
            "host_group_list": groups,
            "page": params.page,
            "per_page": params.per_page
        }
        if params.sort is not None:
            pyload['sort'] = params.sort
            pyload['direction'] = params.direction
        if params.management == "True":
            pyload['management'] = True
        elif params.management == "False":
            pyload['management'] = False
        manager_url, header = make_manager_url(QUERY_HOST)
        header['access_token'] = params.access_token
        result_basic = MyResponse.get_response('POST', manager_url, pyload, header)
        if result_basic.get('code') != SUCCEED:
            print("Query request with bad response.")
            print(result_basic)
            sys.exit(0)
        verbose = True if params.verbose == "True" else False
        if verbose:
            manager_url, header = make_manager_url(QUERY_HOST_DETAIL)
            hosts = []
            for info in result_basic['host_infos']:
                hosts.append(info['host_id'])
            pyload = {
                "host_list": hosts,
            }
            header['access_token'] = params.access_token
            result_details = MyResponse.get_response('POST', manager_url, pyload, header)
            if result_details.get('code') != SUCCEED:
                print("Query request with bad response.")
                print(result_details)
                sys.exit(0)
            for info in result_details['host_infos']:
                for basic_info in result_basic['host_infos']:
                    if info['host_id'] == basic_info['host_id']:
                        basic_info['infos'] = info['infos']
                        break
        host_infos = result_basic.pop('host_infos', [])
        print(result_basic)
        print_row_from_result(host_infos)
        return result_basic

    @staticmethod
    def manage_requests_delete(params):
        """
        Description: Executing delete request
        Args:
            params: Command line parameters
        Returns:
            dict: response of the backend
        """
        hosts = str_split(params.host_list)
        if len(hosts) == 0:
            print("No host will be deleted, because of the empty host list.")
            print("Please check your host list if you want to delete hosts.")
            sys.exit(0)
        name_check(hosts)
        pyload = {
            "host_list": hosts,
        }
        manager_url, header = make_manager_url(DELETE_HOST)
        return cli_request('DELETE', manager_url, pyload, header, params.access_token)
