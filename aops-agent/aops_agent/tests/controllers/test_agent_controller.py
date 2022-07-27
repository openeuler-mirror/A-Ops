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
