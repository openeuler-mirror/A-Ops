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
from adoctor_cli.commands.check_cmd import CheckCommand
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


class TestCheckCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_get_check(self):
        print("Execute the get check test case")
        cmd = CheckCommand()
        args = cmd.parser.parse_args(['check',
                                      '--host_list=h1,h1',
                                      '--check_items=c1,c2',
                                      '--start=20200101-10:10:10',
                                      '--end=20200101-11:00:00',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'start', 'end']
            args_dict = vars(args)
            args_dict['time_range'] = time_check_generate(args_dict['start'], args_dict['end'])
            args_dict['check_items'] = str_split(args_dict['check_items'])
            args_dict['host_list'] = str_split(args_dict['host_list'])
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict, act_res)

    def test_get_check_sort(self):
        print("Execute the get check test case")
        cmd = CheckCommand()
        args = cmd.parser.parse_args(['check',
                                      '--host_list=h1,h1',
                                      '--check_items=c1,c2',
                                      '--start=20200101-10:10:10',
                                      '--end=20200101-11:00:00',
                                      '--sort=check_item',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'start', 'end']
            args_dict = vars(args)
            args_dict['time_range'] = time_check_generate(args_dict['start'], args_dict['end'])
            args_dict['check_items'] = str_split(args_dict['check_items'])
            args_dict['host_list'] = str_split(args_dict['host_list'])
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict, act_res)
