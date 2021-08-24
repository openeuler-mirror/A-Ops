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
from aops_cli.commands.template_cmd import TemplateCommand
from aops_cli.base_cmd import str_split
from aops_utils.readconfig import read_yaml_config_file
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestTemplateCli(unittest.TestCase):
    """
        Unit test for the groupCmd cli.
    """

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_add_template(self):
        print("Execute the add template test case")
        cmd = TemplateCommand()
        args = cmd.parser.parse_args(['template',
                                      '--action=import',
                                      '--template_name=t1',
                                      '--template_content=./test.yaml',
                                      '--description=This is a sample description',
                                      "--access_token=123321"
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = vars(args)
            ignore_list = ['action', 'template_list', 'sort', 'direction', 'sub_parse_name', 'access_token']
            for item in ignore_list:
                args_dict.pop(item)
            args_dict['template_content'] = read_yaml_config_file(args_dict['template_content'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_deletetemplate(self):
        print("Execute the delete template test case")
        cmd = TemplateCommand()
        args = cmd.parser.parse_args(['template',
                                      '--action=delete',
                                      '--template_list=t1,t2,t3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['template_list'])
            args_dict['template_list'] = args_list
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_template(self):
        print("Execute the get template test case")
        cmd = TemplateCommand()
        args = cmd.parser.parse_args(['template',
                                      '--action=query',
                                      '--template_list=t1',
                                      "--access_token=123321",
                                      "--sort=template_name",
                                      "--direction=asc"
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "total_count": 1,
                "total_page": 1,
                "template_infos": [
                    {
                        "template_id": "id1",
                        "template_name": "group1",
                        "description": "xxxxxx",
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['template_list'])
            args_dict['template_list'] = args_list
            param_list = ['access_token', 'sort', 'direction']
            for item in param_list:
                args_dict[item] = vars(args)[item]
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
