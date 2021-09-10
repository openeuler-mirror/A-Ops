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
from aops_cli.commands.host_cmd import HostCommand
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


class TestHostCli(unittest.TestCase):

    def setUp(self):
        self.r = Redirect()
        self.stdout = self.r

    def test_addhost(self):
        print("Execute the add host test case")
        cmd = HostCommand()
        args = cmd.parser.parse_args(['host',
                                      '--action=add',
                                      '--host_name=h1',
                                      '--host_group_name=g1',
                                      '--public_ip=1.1.1.1',
                                      '--ssh_port=22',
                                      '--management=False',
                                      '--username=holo',
                                      '--password=cctv',
                                      "--sudo_password=huawei@123",
                                      "--access_token=123321",
                                      "--key=123"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "host_id": "5c6bf64c-f468-11eb-80a0-3e22fbb33802"
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            ignore_list = ['page', 'per_page','verbose', 'action', 'host_list',
                           'sub_parse_name', 'sort', 'direction', 'access_token']
            args_dict = vars(args)
            for item in ignore_list:
                args_dict.pop(item)
            act_res = mock_get_response.call_args_list[0][0][2]
            self.assertEqual(args_dict.pop('key'), act_res['key'])
            for k in args_dict.keys():
                if args_dict[k] == 'True':
                    key = True
                elif args_dict[k] == 'False':
                    key = False
                else:
                    key = args_dict[k]
                self.assertEqual(key, act_res['host_list'][0][k])

    def test_deletehost(self):
        print("Execute the delete host test case")
        cmd = HostCommand()
        args = cmd.parser.parse_args(['host',
                                      '--action=delete',
                                      '--host_list=h1,h2,h3',
                                      "--access_token=123321"])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_dict['host_list'] = str_split(vars(args)['host_list'])
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_gethost(self):
        print("Execute the get host test case")
        cmd = HostCommand()
        args = cmd.parser.parse_args(['host',
                                      '--action=query',
                                      '--host_group_name=h1',
                                      "--access_token=123321",
                                      "--sort=host_name",
                                      "--direction=asc"
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            expected_res = {
                "code": 200,
                "msg": 'operation succeed',
                "host_infos": [
                    {
                        "host_id": "id1",
                        "host_name": "h1",
                        "host_group_name": "group1"
                    }
                ]
            }
            mock_get_response.return_value = expected_res
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['host_group_name'])
            args_dict['host_group_name'] = args_list
            param_list = ['sort', 'direction']
            for item in param_list:
                args_dict[item] = vars(args)[item]
            host_name = args_dict.pop('host_group_name')
            args_dict['host_group_list'] = host_name
            args_dict['page'] = 1
            args_dict['per_page'] = 20
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])

    def test_gethost_verbose(self):
        print("Execute the get host infos test case")
        cmd = HostCommand()
        args = cmd.parser.parse_args(['host',
                                      '--action=query',
                                      '--host_group_name=h1',
                                      "--access_token=123321",
                                      "--sort=host_name",
                                      "--direction=asc",
                                      "--verbose=True"
                                      ])
        with mock.patch.object(MyResponse, "get_response") as mock_get_response:
            mock_get_response.side_effect = [
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    "host_infos": [
                        {
                            "host_id": "id1",
                            "host_name": "h1",
                            "host_group_name": "group1",
                            "public_ip": "1.1.1.1",
                            "ssh_port": 22,
                            "management": True,
                            "status": "online"
                        }
                    ]
                },
                {
                    "code": 200,
                    "msg": 'operation succeed',
                    "host_infos": [
                        {
                            "host_id": "id1",
                            "infos": {
                                "usage": 0
                            }

                        }
                    ]
                }
            ]
            cmd.do_command(args)
            args_dict = dict()
            args_list = str_split(vars(args)['host_group_name'])
            args_dict['host_group_list'] = args_list
            param_list = ['sort', 'direction', 'page', 'per_page']
            for item in param_list:
                args_dict[item] = vars(args)[item]
            self.assertEqual(args_dict, mock_get_response.call_args_list[0][0][2])
