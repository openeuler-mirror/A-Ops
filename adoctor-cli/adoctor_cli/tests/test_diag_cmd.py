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
from adoctor_cli.commands.diag_cmd import DiagCommand
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


class TestDiagCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_execute_diag_timeout(self):
        print("Execute the execute diag with timeout test case")
        cmd = DiagCommand()
        args = cmd.parser.parse_args(['diag',
                                      '--host_list=h1,h2',
                                      '--tree_list=t1,t2,t3',
                                      '--start=20200101-10:10:10',
                                      '--end=20200101-11:00:00',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            execute_list = [{
                "code": 200,
                "msg": 'operation succeed',
                "task_id": "task1",
                "expected_report_num": 5
            }]
            time_out_dict = {
                "code": 200,
                "msg": '',
                "result": [
                    {
                        'task_id': "task1",
                        'progress': 1
                    }
                ]
            }
            report_dict = {
                "code": 200,
                "msg": "",
                "result": [
                    {
                        "host_id": "host1"
                    }
                ]
            }
            execute_list.append(
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    "task_infos": [
                        {
                            "task_id": "task1",
                            'host_list': ['host1'],
                            'tree_list': ['tree1']
                        }
                    ]
                }
            )
            for i in range(11):
                execute_list.append(time_out_dict)
            execute_list.append(report_dict)
            mock_get_response.side_effect = execute_list
            try:
                cmd.do_command(args)
            except SystemExit as e:
                self.assertEqual(e.code, SystemExit(0).code)

    def test_execute_diag(self):
        print("Execute the excutee diag with test case")
        cmd = DiagCommand()
        args = cmd.parser.parse_args(['diag',
                                      '--host_list=h1,h2',
                                      '--tree_list=t1,t2,t3',
                                      '--start=20200101-10:10:10',
                                      '--end=20200101-11:00:00',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            mock_get_response.side_effect = [
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    "task_id": "task1",
                    "expected_report_num": 5
                },
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    "task_infos": [
                        {
                            "task_id": "task1",
                            'host_list': ['host1'],
                            'tree_list': ['tree1']
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": '',
                    "result": [
                        {
                            'task_id': "task1",
                            'progress': 1
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": '',
                    "result": [
                        {
                            'task_id': "task1",
                            'progress': 2
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": '',
                    "result": [
                        {
                            'task_id': "task1",
                            'progress': 5
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": "",
                    "result": [
                        {
                            "host_id": "host1",
                            "tree_name": "tree1",
                            "task_id": "id1",
                            "report_id": "rid1",
                            "start": "11",
                            "end": "12"
                        }
                    ]
                }]
            cmd.do_command(args)
            ignore_list = ['sub_parse_name', 'access_token', 'start', 'end']
            args_dict = vars(args)
            act_res = mock_get_response.call_args_list[0][0][2]
            args_dict['host_list'] = str_split(args_dict['host_list'])
            args_dict['tree_list'] = str_split(args_dict['tree_list'])
            args_dict['time_range'] = time_check_generate(args_dict['start'], args_dict['end'])
            for item in ignore_list:
                args_dict.pop(item)
            self.assertEqual(args_dict, act_res)
