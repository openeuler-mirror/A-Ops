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
from unittest import mock
from adoctor_cli.commands.stat_cmd import StatCommand
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestStatCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_count_rule(self):
        print("Execute the stat test case with rule")
        cmd = StatCommand()
        args = cmd.parser.parse_args(['stat',
                                      '--action=count',
                                      '--field=check_rule',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "check_rule_count": 100
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = {}
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_count_check(self):
        print("Execute the stat test case with check result")
        cmd = StatCommand()
        args = cmd.parser.parse_args(['stat',
                                      '--action=count',
                                      '--field=check_result',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "results": [
                    {
                        "host_id": "id1",
                        "count": 2
                    },
                    {
                        "host_id": "id2",
                        "count": 5
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = {'host_list': []}
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
