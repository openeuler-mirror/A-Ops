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
import unittest
from adoctor_cli.commands.report_cmd import ReportCommand
from unittest import mock
from aops_utils.validate import str_split
from aops_utils.restful.response import MyResponse
from aops_utils.time_utils import time_check_generate


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestReportCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_get_report(self):
        print("Execute the get report with task id test case")
        cmd = ReportCommand()
        args = cmd.parser.parse_args(['report',
                                      '--action=get',
                                      '--task_id=id1',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "report_id": "5c6bf64c-f468-11eb-80a0-3e22fbb33802"
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'action']
            args_dict = vars(args)
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict['task_id'], act_res['task_id'])

    def test_get_report_with_tree_host(self):
        print("Execute the get report with tree and host test case")
        cmd = ReportCommand()
        args = cmd.parser.parse_args(['report',
                                      '--action=get',
                                      '--tree_list=h1,h2,h3',
                                      '--host_list=id1,id2',
                                      '--start=20200101-10:10:10',
                                      '--end=20200101-11:10:10',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'action', 'start', 'end', 'task_id', 'report_list']
            args_dict = vars(args)
            args_dict['time_range'] = time_check_generate(args_dict['start'], args_dict['end'])
            for item in ignore_list:
                args_dict.pop(item)
            args_dict['tree_list'] = str_split(args_dict['tree_list'])
            args_dict['host_list'] = str_split(args_dict['host_list'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_delete_report(self):
        print("Execute the delete report test case")
        cmd = ReportCommand()
        args = cmd.parser.parse_args(['report',
                                      '--action=delete',
                                      '--report_list=r1,r2',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['report_list'] = str_split(vars(args)['report_list'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
