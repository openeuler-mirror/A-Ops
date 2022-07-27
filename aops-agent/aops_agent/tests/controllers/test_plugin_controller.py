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
import requests
from aops_agent.tests import BaseTestCase


class TestPluginController(BaseTestCase):

    def test_start_plugin_should_return_main_pid_when_input_installed_plugin_name(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "gopher"
        url = f"http://localhost:8080/v1/agent/plugin/start?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert200(response, response.text)

    def test_start_plugin_should_return_failure_info_when_input_installable_plugin_name_but_not_install(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "gopher"
        url = f"http://localhost:8080/v1/agent/plugin/start?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assertEqual(410, response.status_code, response.text)

    def test_start_plugin_should_return_failure_info_when_input_plugin_name_is_not_installable(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "nginx"
        url = f"http://localhost:8080/v1/agent/plugin/start?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)

    def test_start_plugin_should_return_400_when_input_plugin_name_is_none(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = ""
        url = f"http://localhost:8080/v1/agent/plugin/start?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)

    def test_start_plugin_should_return_400_when_with_no_input(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        url = "http://localhost:8080/v1/agent/plugin/start"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)

    def test_stop_plugin_should_return_plugin_stop_success_when_input_installed_plugin_name_and_plugin_is_running(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "gopher"
        url = f"http://localhost:8080/v1/agent/plugin/stop?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert200(response, response.text)

    def test_stop_plugin_should_return_plugin_has_stooped_when_input_installed_plugin_name_and_plugin_is_stopped(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "gopher"
        url = f"http://localhost:8080/v1/agent/plugin/stop?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assertEqual(202, response.status_code, response.text)

    def test_stop_plugin_should_return_failure_info_when_input_installable_plugin_name_but_plugin_not_install(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "gopher"
        url = f"http://localhost:8080/v1/agent/plugin/stop?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assertEqual(410, response.status_code, response.text)

    def test_stop_plugin_should_return_failure_info_when_input_plugin_name_is_not_installable(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = "docker"
        url = f"http://localhost:8080/v1/agent/plugin/stop?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)

    def test_stop_plugin_should_return_400_when_with_input_plugin_name_is_none(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        plugin_name = ""
        url = f"http://localhost:8080/v1/agent/plugin/stop?plugin_name={plugin_name}"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)

    def test_stop_plugin_should_return_400_when_with_no_input(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        url = "http://localhost:8080/v1/agent/plugin/stop"
        response = requests.get(url, headers=headers)
        self.assert400(response, response.text)
