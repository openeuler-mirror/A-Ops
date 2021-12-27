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
Description: check method's entrance for custom commands
Class:CheckCommand
"""
from adoctor_cli.base_cmd import BaseCommand
from aops_utils.restful.helper import make_check_url
from aops_utils.conf.constant import CHECK_GET_RESULT
from aops_utils.time_utils import time_transfer
from aops_utils.validate import name_check, str_split
from aops_utils.cli_utils import add_page, add_access_token, add_query_args
from aops_utils.cli_utils import add_start_and_end, request_without_print, pretty_json


class CheckCommand(BaseCommand):
    """
    Description: start the check part
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='check',
                            help_desc="check operations")
        self.sub_parse.add_argument(
            '--host_list',
            nargs='?',
            type=str,
            help='host ips')

        self.sub_parse.add_argument(
            '--check_items',
            nargs='?',
            type=str,
            help='ckeck items')

        add_start_and_end(self.sub_parse)
        add_access_token(self.sub_parse)
        add_query_args(self.sub_parse, ['check_item', 'start', 'end'])
        add_page(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        """
        self.manage_requests_check(params)

    @staticmethod
    def manage_requests_check(params):
        """
        Description: Executing check command
        Args:
            params: Command line parameters
        Returns:
            dict: body of response
        """

        hosts = str_split(params.host_list)
        checks = str_split(params.check_items)
        name_check(hosts)
        name_check(checks)
        time_list = time_transfer(params.start, params.end)

        pyload = {
            "time_range": [time_list[0], time_list[1]],
            "check_items": checks,
            "host_list": hosts,
            "page": params.page,
            "per_page": params.per_page
        }
        if params.sort is not None:
            pyload['sort'] = params.sort
            pyload['direction'] = params.direction
        check_url, header = make_check_url(CHECK_GET_RESULT)
        result = request_without_print('POST', check_url, pyload, header, params.access_token)
        print(pretty_json(result))
