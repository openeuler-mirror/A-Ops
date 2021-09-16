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
from adoctor_cli.commands.fault_tree_cmd import FaultreeCommand
from unittest import mock
from aops_utils.validate import str_split
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestTreeCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_add_tree(self):
        print("Execute the add tree test case")
        cmd = FaultreeCommand()
        args = cmd.parser.parse_args(['faultree',
                                      '--action=add',
                                      '--tree_list=tree1',
                                      '--conf=./right_tree2.xls',
                                      '--description=Null description',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "tree_id": "5c6bf64c-f468-11eb-80a0-3e22fbb33802"
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'action', ]
            args_dict = vars(args)
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict['tree_list'], act_res['trees'][0]['tree_name'])
            self.assertEqual(args_dict['description'], act_res['trees'][0]['description'])

    def test_delete_tree(self):
        print("Execute the delete tree test case")
        cmd = FaultreeCommand()
        args = cmd.parser.parse_args(['faultree',
                                      '--action=delete',
                                      '--tree_list=h1,h2,h3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['tree_list'] = str_split(vars(args)['tree_list'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_tree(self):
        print("Execute the get tree test case")
        cmd = FaultreeCommand()
        args = cmd.parser.parse_args(['faultree',
                                      '--action=get',
                                      '--tree_list=h1',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "trees": [
                    {
                        "tree_name": "tree1",
                        "tree_content": {"tree_ele": 'ele',
                                         "tree_eee": 'eee'},
                        "description": "",
                        "tag": ['winwin'],
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['tree_list'] = str_split(vars(args)['tree_list'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
