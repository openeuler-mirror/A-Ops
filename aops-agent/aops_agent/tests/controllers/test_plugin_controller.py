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
from unittest import mock

from aops_agent.conf.status import StatusCode, SUCCESS, FILE_NOT_FOUND
from aops_agent.tests import BaseTestCase
from aops_agent.manages.token_manage import TokenManage
from aops_agent.manages.plugin_manage import Plugin

header = {
    "Content-Type": "application/json; charset=UTF-8"
}

header_with_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "13965d8302b5246a13352680d7c8e602"
}

header_with_incorrect_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "13965d8302b5246a13352680d7c8e602Ss"
}


class TestPluginController(BaseTestCase):
    def setUp(self) -> None:
        TokenManage.set_value('13965d8302b5246a13352680d7c8e602')

    @mock.patch.object(Plugin, 'start_service')
    def test_start_plugin_should_return_200_when_input_installed_plugin_name_with_correct_token(self,
                                                                                                mock_start_service):
        plugin_name = "gopher"
        mock_start_service.return_value = SUCCESS, StatusCode.make_response_body(SUCCESS)
        response = self.client.get(f'/v1/agent/plugin/start?plugin_name={plugin_name}', headers=header_with_token)
        self.assert200(response, response.text)

    @mock.patch.object(Plugin, 'start_service')
    def test_start_plugin_should_return_410_when_input_plugin_name_is_not_installed_with_correct_token(
            self, mock_start_service):
        plugin_name = "gopher"
        mock_start_service.return_value = SUCCESS, StatusCode.make_response_body(FILE_NOT_FOUND)
        response = self.client.get(f'/v1/agent/plugin/start?plugin_name={plugin_name}', headers=header_with_token)
        self.assertIn('410', response.text)

    def test_start_plugin_should_return_param_error_when_input_plugin_name_is_not_supported_with_correct_token(self):
        plugin_name = "nginx"
        response = self.client.get(f'/v1/agent/plugin/start?plugin_name={plugin_name}', headers=header_with_token)
        self.assertIn('1000', response.text)

    def test_start_plugin_should_return_param_error_when_input_plugin_name_is_none_with_correct_token(self):
        response = self.client.get('/v1/agent/plugin/start?plugin_name=', headers=header_with_token)
        self.assertIn('1000', response.text)

    def test_start_plugin_should_return_400_when_input_none_with_correct_token(self):
        response = self.client.get('/v1/agent/plugin/start', headers=header_with_token)
        self.assert400(response, response.text)

    def test_start_plugin_should_return_401_when_input_installed_plugin_name_with_incorrect_token(self):
        response = self.client.get('/v1/agent/plugin/start?plugin_name=gopher', headers=header_with_incorrect_token)
        self.assert401(response, response.text)

    def test_start_plugin_should_return_401_when_input_installed_plugin_name_with_no_token(self):
        response = self.client.get('/v1/agent/plugin/start?plugin_name=gopher')
        self.assert401(response, response.text)

    def test_start_plugin_should_return_405_when_request_by_other_method(self):
        response = self.client.post('/v1/agent/plugin/start?plugin_name=gopher')
        self.assert405(response, response.text)

    @mock.patch("aops_agent.controllers.plugin_controller.INFORMATION_ABOUT_RPM_SERVICE")
    def test_start_plugin_should_return_500_when_input_installed_plugin_name_but_has_no_info_with_correct_token(self, mock_info):
        plugin_name = "gopher"
        mock_info = {}
        response = self.client.get(f'/v1/agent/plugin/start?plugin_name={plugin_name}', headers=header_with_token)
        self.assertIn("500", response.text)

    @mock.patch.object(Plugin, 'stop_service')
    def test_stop_plugin_should_return_200_when_input_installed_plugin_name_with_correct_token(self, mock_stop_service):
        mock_stop_service.return_value = SUCCESS, StatusCode.make_response_body(SUCCESS)
        plugin_name = "gopher"
        response = self.client.get(f'/v1/agent/plugin/stop?plugin_name={plugin_name}', headers=header_with_token)
        self.assert200(response, response.text)

    @mock.patch.object(Plugin, 'stop_service')
    def test_stop_plugin_should_return_410_when_input_plugin_name_is_not_installed_with_correct_token(self,
                                                                                                      mock_stop_service):
        mock_stop_service.return_value = SUCCESS, StatusCode.make_response_body(SUCCESS)
        plugin_name = "gopher"
        response = self.client.get(f'/v1/agent/plugin/stop?plugin_name={plugin_name}', headers=header_with_token)
        self.assert200(response, response.text)

    def test_stop_plugin_should_return_param_error_when_input_plugin_name_is_not_supported_with_correct_token(self):
        plugin_name = "nginx"
        response = self.client.get(f'/v1/agent/plugin/stop?plugin_name={plugin_name}', headers=header_with_token)
        self.assertIn('1000', response.text)

    def test_stop_plugin_should_return_param_error_when_input_plugin_name_is_none_with_correct_token(self):
        response = self.client.get('/v1/agent/plugin/stop?plugin_name=', headers=header_with_token)
        self.assertIn('1000', response.text)

    def test_stop_plugin_should_return_400_when_input_none_with_correct_token(self):
        response = self.client.get('/v1/agent/plugin/stop', headers=header_with_token)
        self.assert400(response, response.text)

    def test_stop_plugin_should_return_401_when_input_installed_plugin_name_with_incorrect_token(self):
        response = self.client.get('/v1/agent/plugin/stop?plugin_name=gopher', headers=header_with_incorrect_token)
        self.assert401(response, response.text)

    def test_stop_plugin_should_return_401_when_input_installed_plugin_name_with_no_token(self):
        response = self.client.get('/v1/agent/plugin/stop?plugin_name=gopher')
        self.assert401(response, response.text)

    def test_stop_plugin_should_return_405_when_request_by_other_method(self):
        response = self.client.post('/v1/agent/plugin/stop?plugin_name=gopher')
        self.assert405(response, response.text)

    @mock.patch("aops_agent.controllers.plugin_controller.INFORMATION_ABOUT_RPM_SERVICE")
    def test_stop_plugin_should_return_500_when_input_installed_plugin_name_but_has_no_info_with_correct_token(self, mock_info):
        plugin_name = "gopher"
        mock_info = {}
        response = self.client.get(f'/v1/agent/plugin/stop?plugin_name={plugin_name}', headers=header_with_token)
        self.assertIn("500", response.text)
