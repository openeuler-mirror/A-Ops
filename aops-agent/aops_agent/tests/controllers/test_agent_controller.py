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
import requests

from aops_agent.manages.token_manage import TokenManage
from aops_agent.tests import BaseTestCase


class TestAgentController(BaseTestCase):
    def test_get_host_info_should_return_os_info_when_input_correct_token(self):
        """
            correct request method with correct token
        """
        url = "http://localhost:8080/v1/agent/basic/info"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        response = requests.get(url, headers=headers)
        self.assert200(response, response.text)

    def test_get_host_info_should_return_400_when_with_no_token(self):
        """
            correct request method with no token
        """
        url = "http://localhost:8080/v1/agent/basic/info"
        response = requests.get(url)
        self.assert400(response, response.text)

    def test_get_host_info_should_return_401_when_input_incorrect_token(self):
        """
            correct request method with incorrect token
        """
        url = "http://localhost:8080/v1/agent/basic/info"
        headers = {'Content-Type': 'application/json', 'access_token': ''}
        response = requests.get(url, headers=headers)
        self.assert401(response, response.text)

    def test_change_collect_items_should_only_return_change_success_when_input_correct(self):
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assert200(response, response.text)

    def test_change_collect_items_should_return_change_success_and_failure_when_input_unsupported_items(self):
        """
           some probe is incorrect
        """
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assert200(response, response.text)

    def test_change_collect_items_should_return_not_support_when_input_unsupported_plugin(self):
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        data = {
            "gopher2": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assert200(response, response.text)

    def test_change_collect_items_should_return_all_result_when_input_installed_plugin_and_unsupported_plugin(self):
        """
            Returns:
                unsupported plugin: not support,
                installed plugin: failure list and success list

        """
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
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
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assert200(response, response.text)

    def test_change_collect_items_should_return_400_when_input_incorrect(self):
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        data = {
            "gopher": {
                "redis": 1,
                "system_inode": "on",
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assert400(response, response.text)

    def test_change_collect_items_should_return_400_when_with_no_input(self):
        url = "http://localhost:8080/v1/agent/collect/items/change"
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        response = requests.post(url, headers=headers)
        self.assert400(response, response.text)


class TestGetApplicationInfo(BaseTestCase):
    headers = {'Content-Type': 'application/json'}
    headers_with_token = {'Content-Type': 'application/json', 'access_token': '13965d8302b5246a13352680d7c8e602'}
    headers_with_incorrect_token = {'Content-Type': 'application/json',
                                    'access_token': '213965d8302b5246a13352680d7c8e602'}

    def test_get_application_info_should_return_target_app_running_info_when_with_correct_token(self):
        TokenManage.set_value('13965d8302b5246a13352680d7c8e602')
        with mock.patch('aops_agent.controllers.agent_controller.plugin_status_judge') as mock_plugin_status:
            mock_plugin_status.return_value = 'Active: active (running)'
            response = self.client.get('/v1/agent/application/info', headers=self.headers_with_token)
            self.assert200(response, response.text)

    def test_get_application_info_should_return_401_when_with_incorrect_token(self):
        headers = {'Content-Type': 'application/json', 'access_token': '123456'}
        response = self.client.get('/v1/agent/application/info', headers=headers)
        self.assert401(response, response.text)

    def test_get_application_info_should_return_400_when_with_no_token(self):
        response = self.client.get('/v1/agent/application/info')
        self.assert400(response, response.text)

    def test_get_application_info_should_return_405_when_request_by_incorrect_method(self):
        response = self.client.post('/v1/agent/application/info')
        self.assert405(response, response.text)

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    @mock.patch('aops_agent.controllers.agent_controller.get_file_info')
    def test_collect_file_should_return_file_content_when_input_correct_file_path_with_token(self,
                                                                                             mock_file_info,
                                                                                             mock_isfile,
                                                                                             mock_exists
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
        data = ['test1', 'test2']
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertTrue(json.loads(response.text).get('infos')[0].get('content'), response.text)

    @mock.patch('aops_agent.controllers.agent_controller.get_file_info')
    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_exist(self,
                                                                                    mock_isfile,
                                                                                    mock_exists,
                                                                                    mock_file_info
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
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(json.loads(response.text).get('fail_files'), ['test2'], response.text)

    @mock.patch.object(os.path, 'isfile')
    @mock.patch.object(os.path, 'exists')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_a_file(self, mock_exists, mock_isfile):
        mock_exists.return_value = True
        mock_isfile.side_effect = [False, False]
        data = ['test1', 'test2']
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(['test1', 'test2'], json.loads(response.text).get('fail_files'), response.text)

    def test_collect_file_should_return_401_when_input_correct_file_path_with_incorrect_token(self):
        data = ['test1']
        response = self.client.post('/v1/agent/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_incorrect_token)
        self.assert401(response, response.text)

    def test_collect_file_should_return_400_when_input_correct_file_path_with_no_token(self):
        data = ['test1']
        response = self.client.post('/v1/agent/file/collect', data=json.dumps(data), headers=self.headers)
        self.assert400(response, response.text)

    def test_collect_file_should_return_400_when_no_input_with_token(self):
        response = self.client.post('/v1/agent/file/collect', headers=self.headers)
        self.assert400(response, response.text)

    def test_collect_file_should_return_400_when_input_incorrect_data_with_token(self):
        data = [2333]
        response = self.client.post('/v1/agent/file/collect', data=json.dumps(data), headers=self.headers)
        self.assert400(response, response.text)

    def test_collect_file_should_return_405_when_requset_by_get(self):
        data = ['test1']
        response = self.client.get('/v1/agent/file/collect', data=json.dumps(data), headers=self.headers)
        self.assert405(response, response.text)
