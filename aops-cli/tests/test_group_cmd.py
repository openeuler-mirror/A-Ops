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
from aops_cli.base_cmd import str_split
from aops_cli.commands.group_cmd import GroupCommand
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestGroupCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_add_group(self):
        print("Execute the add host group test case")
        cmd = GroupCommand()
        args = cmd.parser.parse_args(['group',
                                      '--action=add',
                                      '--host_group_name=g1',
                                      '--description=This is a sample description',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "host_group_id": "5c6bf64c-f468-11eb-80a0-3e22fbb33802"
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = vars(args)
            ignore_list = ['access_token', 'action', 'host_group_list', 'sub_parse_name']
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict, act_res)

    def test_delete_group(self):
        print("Execute the delete host group test case")
        cmd = GroupCommand()
        args = cmd.parser.parse_args(['group',
                                      '--action=delete',
                                      '--host_group_list=g1,g2,g3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['host_group_list'])
            args_dict['host_group_list'] = args_list
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_host_group(self):
        print("Execute the get host group test case")
        cmd = GroupCommand()
        args = cmd.parser.parse_args(['group',
                                      '--action=query',
                                      '--access_token=111221'
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "total_count": 1,
                "total_page": 1,
                "host_group_infos": [
                    {
                        "host_group_id": "id1",
                        "host_group_name": "group1",
                        "description": "xxxxxx",
                        "host_count": 11
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
