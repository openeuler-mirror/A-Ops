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
import pathlib as pl
import unittest
from unittest import mock
from adoctor_cli.commands.check_rule_cmd import CheckRuleCommand
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


class TestCheckRuleCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_add_check_rule(self):
        print("Execute the add check rule test case")
        cmd = CheckRuleCommand()
        args = cmd.parser.parse_args(['checkrule',
                                      '--action=add',
                                      '--conf=./test.json',
                                      '--access_token=123321'])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "success_list": ["item1"],
                "fail_list": []
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['access_token', 'action', 'sub_parse_name']
            args_dict = vars(args)
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            json_content = {
                'check_items': [
                    {'check_item': 'check_item996',
                     'condition': '$0>1',
                     'data_list': [{'label': {'cpu': '1', 'mode': 'irq'},
                                    'name': 'node_cpu_seconds_total',
                                    'type': 'kpi'}],
                     'description': 'aaa',
                     'plugin': ''}]}
            self.maxDiff = None
            self.assertEqual(json_content, act_res)

    def test_delete_check_rule(self):
        print("Execute the delete check rule test case")
        cmd = CheckRuleCommand()
        args = cmd.parser.parse_args(['checkrule',
                                      '--action=delete',
                                      '--check_items=r1,r2,r3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['check_items'] = str_split(vars(args)['check_items'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_check_rule(self):
        print("Execute the get check rule test case")
        cmd = CheckRuleCommand()
        args = cmd.parser.parse_args(['checkrule',
                                      '--action=get',
                                      '--check_items=h1,h2',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "check_items": {
                    'check_items': [
                        {'check_item': 'check_item996',
                         'condition': '$0>1',
                         'data_list': [{'label': {'cpu': '1', 'mode': 'irq'},
                                        'name': 'node_cpu_seconds_total',
                                        'type': 'kpi'}],
                         'description': 'aaa',
                         'plugin': ''}]}
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['check_items'] = str_split(vars(args)['check_items'])
            args_dict['page'] = 1
            args_dict['per_page'] = 20
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_check_rule_export(self):
        print("Execute the export check rule test case")
        cmd = CheckRuleCommand()
        args = cmd.parser.parse_args(['checkrule',
                                      '--action=get',
                                      '--check_items=h1,h2',
                                      '--export=./test.json',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "check_items":  [
                        {'check_item': 'check_item996',
                         'condition': '$0>1',
                         'data_list': [{'label': {'cpu': '1', 'mode': 'irq'},
                                        'name': 'node_cpu_seconds_total',
                                        'type': 'kpi'}],
                         'description': 'aaa',
                         'plugin': ''}]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = {'check_items': str_split(vars(args)['check_items']), 'page': 1, 'per_page': 20}
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
            path = pl.Path(vars(args)['export'])
            self.assertTrue(path.is_file())
