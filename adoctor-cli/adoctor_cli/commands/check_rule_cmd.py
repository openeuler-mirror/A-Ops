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
Description: checkrule method's entrance for custom commands
Class:CheckRuleCommand
"""
import json
import sys

from adoctor_cli.base_cmd import BaseCommand
from aops_utils.restful.helper import make_check_url
from aops_utils.readconfig import read_json_config_file
from aops_utils.conf.constant import CHECK_IMPORT_RULE, CHECK_GET_RULE, CHECK_DELETE_RULE
from aops_utils.validate import name_check, str_split
from aops_utils.cli_utils import add_page, cli_request, add_access_token


class CheckRuleCommand(BaseCommand):
    """
    Description: checkrule's operations
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='checkrule',
                            help_desc="checkrule's operations")
        self.sub_parse.add_argument(
            '--action',
            help='check rule actions: add, delete, get',
            nargs='?',
            type=str,
            required=True,
            choices=['add', 'delete', 'get'])

        self.sub_parse.add_argument(
            '--check_items',
            help='check items',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--conf',
            help='.json config file',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--export',
            help='export path of the result',
            nargs='?',
            type=str)

        add_access_token(self.sub_parse)
        add_page(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        """

        action = params.action

        action_dict = {
            'add': self.manage_requests_import_check_rule,
            'delete': self.manage_requests_delete_check_rule,
            'get': self.manage_requests_get_check_rule
        }

        action_dict.get(action)(params)

    @staticmethod
    def manage_requests_import_check_rule(params):
        """
        Description: Executing import command
        Args:
            params(namespace): params of the cli
        Returns:
            dict: body of response
        """
        conf_json = read_json_config_file(params.conf)
        if conf_json is None:
            print("Invalid json config file, please import valid json file and try again")
            sys.exit(0)
        pyload = conf_json
        check_url, header = make_check_url(CHECK_IMPORT_RULE)
        return cli_request('POST', check_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_get_check_rule(params):
        """
        Description: Executing get command
        Args:
            params(namespace): params of the cli
        Returns:
            dict： body of response
        """
        checks = str_split(params.check_items)
        name_check(checks)
        pyload = {
            "check_items": checks,
            "page": params.page,
            "per_page": params.per_page
        }

        check_url, header = make_check_url(CHECK_GET_RULE)
        res = cli_request('POST', check_url, pyload, header, params.access_token)
        path = params.export
        if path is None:
            return res
        with open(path, 'w', encoding='utf-8') as file:
            out_file = {'check_items': res['check_items']}
            file.write(json.dumps(out_file))
        return res

    @staticmethod
    def manage_requests_delete_check_rule(params):
        """
        Description: Executing delete command
        Args:
            params(namespace): params of the cli
        Returns:
            dict： body of response
        """
        checks = str_split(params.check_items)
        name_check(checks)
        pyload = {"check_items": checks}

        check_url, header = make_check_url(CHECK_DELETE_RULE)
        return cli_request('DELETE', check_url, pyload, header, params.access_token)
