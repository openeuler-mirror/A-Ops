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
from __future__ import absolute_import

import json
from unittest import mock
import os

from aops_agent.conf.status import TOKEN_ERROR, SUCCESS, PARAM_ERROR
from aops_agent.manages.token_manage import TokenManage
from aops_agent.tests import BaseTestCase


class TestAgentController(BaseTestCase):
    headers = {'Content-Type': 'application/json'}
    headers_with_token = {'Content-Type': 'application/json', 'access_token': 'hdahdahiudahud'}
    headers_with_incorrect_token = {'Content-Type': 'application/json',
                                    'access_token': '213965d8302b5246a13352680d7c8e602'}

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_host_info_should_return_os_info_when_request_by_correct_token(self, mock_token):
        """
            correct request method with correct token
        """
        mock_token.return_value = 'hdahdahiudahud'
        url = "v1/agent/basic/info"
        response = self.client.get(url, headers=self.headers_with_token)
        self.assertEqual(SUCCESS, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_host_info_should_return_400_when_with_no_token(self, mock_token):
        """
            correct request method with no token
        """
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/basic/info"
        response = self.client.get(url)
        self.assert400(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_host_info_should_return_token_error_when_input_incorrect_token(self, mock_token):
        """
            correct request method with incorrect token
        """
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/basic/info"
        response = self.client.get(url, headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_host_info_should_return_405_when_request_by_other_method(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/basic/info"
        response = self.client.post(url, headers=self.headers_with_token)
        self.assert405(response)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_only_return_change_success_when_input_correct(self,
                                                                                       mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_return_change_success_and_failure_when_input_unsupported_items(
            self, mock_token):
        """
           some probe is incorrect
        """
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_return_not_support_when_input_unsupported_plugin(self,
                                                                                          mock_token):
        url = "http://localhost:12000/v1/agent/collect/items/change"
        data = {
            "gopher2": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_return_all_result_when_input_installed_plugin_and_unsupported_plugin(
            self, mock_token):
        """
            Returns:
                unsupported plugin: not support,
                installed plugin: failure list and success list

        """
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            },
            "gopher2": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_return_param_error_when_input_incorrect(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/collect/items/change"
        data = {
            "gopher": {
                "redis": 1,
                "system_inode": "on",
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assertEqual(PARAM_ERROR, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_change_collect_items_should_return_param_error_when_with_no_input(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        url = "http://localhost:12000/v1/agent/collect/items/change"
        response = self.client.post(url, headers=self.headers_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_application_info_should_return_target_app_running_info_when_with_correct_token(
            self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        with mock.patch(
                'aops_agent.controllers.agent_controller.plugin_status_judge') as mock_plugin_status:
            mock_plugin_status.return_value = 'Active: active (running)'
            response = self.client.get('/v1/agent/application/info',
                                       headers=self.headers_with_token)
            self.assert200(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_application_info_should_return_token_error_when_with_incorrect_token(self,
                                                                                      mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.get('/v1/agent/application/info',
                                   headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_application_info_should_return_400_when_with_no_token(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.get('/v1/agent/application/info')
        self.assert400(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_get_application_info_should_return_405_when_request_by_incorrect_method(self,
                                                                                     mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/application/info')
        self.assert405(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    @mock.patch('aops_agent.controllers.agent_controller.get_file_info')
    def test_collect_file_should_return_file_content_when_input_correct_file_path_with_token(self,
                                                                                             mock_file_info,
                                                                                             mock_isfile,
                                                                                             mock_exists,
                                                                                             mock_token
                                                                                             ):
        mock_file_info.return_value = {"path": "file_path",
                                       "file_attr": {
                                           "mode": "0755",
                                           "owner": "owner",
                                           "group": "group"
                                       },
                                       "content": "content"
                                       }
        mock_isfile.return_value = True
        mock_exists.return_value = True
        mock_token.return_value = 'hdahdahiudahud'
        data = ['test1', 'test2']
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertTrue(json.loads(response.text).get('infos')[0].get('content'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    @mock.patch('aops_agent.controllers.agent_controller.get_file_info')
    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_exist(self,
                                                                                    mock_isfile,
                                                                                    mock_exists,
                                                                                    mock_file_info,
                                                                                    mock_token
                                                                                    ):
        mock_isfile.side_effect = [True, True]
        mock_exists.side_effect = [True, False]
        data = ['test1', 'test2']
        mock_file_info.return_value = {"path": "file_path",
                                       "file_attr": {
                                           "mode": "0755",
                                           "owner": "owner",
                                           "group": "group"
                                       },
                                       "content": "content"
                                       }
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(json.loads(response.text).get('fail_files'), ['test2'], response.text)

    @mock.patch.object(TokenManage, 'get_value')
    @mock.patch.object(os.path, 'isfile')
    @mock.patch.object(os.path, 'exists')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_a_file(self,
                                                                                     mock_exists,
                                                                                     mock_isfile,
                                                                                     mock_token):
        mock_exists.return_value = True
        mock_isfile.side_effect = [False, False]
        data = ['test1', 'test2']
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(['test1', 'test2'], json.loads(response.text).get('fail_files'),
                         response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_collect_file_should_return_token_error_when_input_correct_file_path_with_incorrect_token(
            self, mock_token):
        data = ['test1']
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_collect_file_should_return_400_when_input_correct_file_path_with_no_token(self,
                                                                                       mock_token):
        data = ['test1']
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/file/collect', data=json.dumps(data),
                                    headers=self.headers)
        self.assert400(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_collect_file_should_return_400_when_no_input_with_token(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.post('/v1/agent/file/collect', headers=self.headers)
        self.assert400(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_collect_file_should_return_400_when_input_incorrect_data_with_token(self, mock_token):
        mock_token.return_value = 'hdahdahiudahud'
        data = [2333]
        response = self.client.post('/v1/agent/file/collect', data=json.dumps(data),
                                    headers=self.headers)
        self.assert400(response, response.text)

    @mock.patch.object(TokenManage, 'get_value')
    def test_collect_file_should_return_405_when_requset_by_get(self, mock_token):
        data = ['test1']
        mock_token.return_value = 'hdahdahiudahud'
        response = self.client.get('/v1/agent/file/collect', data=json.dumps(data),
                                   headers=self.headers)
        self.assert405(response, response.text)
