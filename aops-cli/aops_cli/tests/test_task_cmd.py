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
from aops_utils.validate import str_split
from aops_cli.commands.task_cmd import TaskCommand
from aops_utils.restful.response import MyResponse


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getValue(self):
        return self._content


class TestTaskCli(unittest.TestCase):
    """
        Unit test for the groupCmd cli.
    """

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_add_task(self):
        print("Execute the add task test case")
        cmd = TaskCommand()
        args = cmd.parser.parse_args(['task',
                                      '--action=generate',
                                      '--task_name=t1',
                                      '--template_name=tl1,tl2,tl3',
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
            ignore_list = ['action', 'task_list', 'sub_parse_name', 'sort', 'direction', "access_token", 'page',
                           'per_page']
            for item in ignore_list:
                args_dict.pop(item)
            args_dict['template_name'] = str_split(vars(args)['template_name'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_delete_task(self):
        print("Execute the delete task test case")
        cmd = TaskCommand()
        args = cmd.parser.parse_args(['task',
                                      '--action=delete',
                                      '--task_list=t1,t2,t3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed'
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['task_list'] = str_split(vars(args)['task_list'])

            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_get_task(self):
        print("Execute the get task test case")
        cmd = TaskCommand()
        args = cmd.parser.parse_args(['task',
                                      '--action=query',
                                      '--task_list=t1',
                                      "--access_token=123321",
                                      "--sort=task_name",
                                      "--direction=asc"
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "total_count": 1,
                "total_page": 1,
                "task_infos": [
                    {
                        "task_id": "id1",
                        "task_name": "task1",
                        "description": "xxxxxx",
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['task_list'])
            args_dict['task_list'] = args_list
            args_dict['page'] = 1
            args_dict['per_page'] = 20
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    @mock.patch('builtins.input')
    def test_execute_task(self, mock_input):
        print("Execute the execute task test case")
        cmd = TaskCommand()
        args = cmd.parser.parse_args(['task',
                                      '--action=execute',
                                      '--task_list=t1',
                                      "--access_token=123321"])
        mock_input.return_value = 'y'
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            mock_get_response.side_effect = [
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    'task_infos': [
                        {
                            "task_id": "95c3e692ff3811ebbcd3a89d3a259eef",
                            "task_name": "Default deployment",
                            "username": "admin",
                            "description": " The default task for installing: zookeeper, kafka, prometheus, node_exporter, mysql, elasticsearch, fluentd, gala-spider, gala-gopher, gala-ragdoll.\n",
                            "host_list": [
                                {
                                    "host_name": "90.90.64.64",
                                    "host_id": "11111"
                                },
                                {
                                    "host_name": "90.90.64.66",
                                    "host_id": "11111"
                                },
                                {
                                    "host_name": "90.90.64.65",
                                    "host_id": "33333"
                                }
                            ]
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": 'operation succeed'
                }
            ]
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['task_list'])
            args_dict['task_list'] = args_list
            args_dict['page'] = 1
            args_dict['per_page'] = 20
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
