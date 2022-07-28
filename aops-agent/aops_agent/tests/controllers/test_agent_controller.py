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

import requests

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
