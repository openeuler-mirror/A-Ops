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
from aops_cli.commands.account_cmd import AccountCommand
from aops_cli.base_cmd import str_split
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestAccountCli(unittest.TestCase):
    """
        Unit test for the groupCmd cli.
    """

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_login(self):
        print("Execute the login test case")
        cmd = AccountCommand()
        args = cmd.parser.parse_args(['account',
                                      '--action=login',
                                      '--username=woshishui',
                                      '--password=whoami'
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = vars(args)
            ignore_list = ['key', 'action', 'access_token', 'sub_parse_name']
            for k in ignore_list:
                args_dict.pop(k)
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
