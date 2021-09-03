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
Description: report method's entrance for custom commands
Class:ReportCommand
"""

from adoctor_cli.base_cmd import BaseCommand, str_split, cli_request
from adoctor_cli.base_cmd import add_access_token, add_start_and_end
from aops_utils.restful.helper import make_diag_url
from aops_utils.conf.constant import DIAG_GET_REPORT_LIST, DIAG_DELETE_REPORT, DIAG_GET_REPORT
from aops_utils.time_utils import time_check_generate


class ReportCommand(BaseCommand):
    """
    Description: start the report part
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='report',
                            help_desc="report's operations")

        self.sub_parse.add_argument(
            '--action',
            help='report actions: get, delete',
            nargs='?',
            type=str,
            required=True,
            choices=['get', 'delete'])

        self.sub_parse.add_argument(
            '--host_list',
            help='host ips',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--tree_list',
            help='diagnosis trees',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--report_list',
            help="ids of reports",
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--task_id',
            help="ids of tasks",
            nargs='?',
            type=str)

        add_start_and_end(self.sub_parse)
        add_access_token(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters

        """

        starttime = params.start
        endtime = params.end
        time_list = time_check_generate(starttime, endtime)
        action = params.action

        action_dict = {
            'delete': self.manage_requests_delete_report,  # /manage/delete_report
            'get': self.manage_requests_get_report  # /manage/get_report
        }
        kwargs = {
            "params": params,
            "time_list": time_list
        }
        action_dict.get(action)(**kwargs)

    @staticmethod
    def manage_requests_get_report(**kwargs):
        """
        Description: Executing get report command
        Args:
            kwargs(dict): dict of the params and time_list
        Returns:
            dict: body of response
        """
        params = kwargs.get('params')
        time_list = kwargs.get('time_list')
        pyload = {}
        if params.report_list is not None:
            pyload['report_list'] = str_split(params.report_list)
            diag_url, header = make_diag_url(DIAG_GET_REPORT)
            return cli_request('POST', diag_url, pyload, header, params.access_token)
        if params.host_list is not None:
            pyload['host_list'] = str_split(params.host_list)
        if params.tree_list is not None:
            pyload['tree_list'] = str_split(params.tree_list)
        if params.task_id is not None:
            pyload['task_id'] = params.task_id
        pyload["time_range"] = time_list

        diag_url, header = make_diag_url(DIAG_GET_REPORT_LIST)
        return cli_request('POST', diag_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_delete_report(**kwargs):
        """
        Description: Executing delete report command
        Args:
            kwargs(dict): dict of params and time_list
        Returns:
            dict: body of response
        """
        params = kwargs.get('params')
        reports = str_split(params.report_list) if params.report_list is not None else []

        pyload = {
            "report_list": reports
        }
        diag_url, header = make_diag_url(DIAG_DELETE_REPORT)
        return cli_request('DELETE', diag_url, pyload, header, params.access_token)
