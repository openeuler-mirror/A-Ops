#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import unittest
import warnings

import responses
from aops_agent.manages.command_manage import Command


class TestRegister(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter('ignore', ResourceWarning)

    @responses.activate
    def test_register_should_return_200_when_input_correct(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "agent_port": "12000"
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": 200},
                      status=200,
                      content_type='application/json'
                      )
        data = Command.register(input_data)
        self.assertEqual(200, data)

    def test_register_should_return_400_when_input_web_username_is_null(self):
        input_data = {
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_web_username_is_not_string(self):
        input_data = {
            "web_username": 12345,
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_web_password_is_null(self):
        input_data = {
            "web_username": "admin",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_web_password_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": 123456,
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_host_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_host_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": 12345,
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_host_group_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_host_group_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": True,
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_management_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_management_is_not_boolean(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": "string",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_manager_ip_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_manager_ip_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_manager_port_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_manager_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": 80
        }
        data = Command.register(input_data)
        self.assertEqual(400, data)

    def test_register_should_return_400_when_input_agent_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "agent_port": 11000
        }
        data = Command.register(input_data)
        self.assertEqual(data, 400)

    @responses.activate
    def test_register_should_return_200_when_input_with_no_agent_port(self):
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": 200},
                      status=200,
                      content_type='application/json'
                      )
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
        }
        data = Command.register(input_data)
        self.assertEqual(200, data)
