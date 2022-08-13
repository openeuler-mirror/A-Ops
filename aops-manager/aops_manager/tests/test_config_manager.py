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
import json

import requests
from flask import Flask
import responses

import aops_manager
from aops_manager.account_manager.cache import UserCache, UserInfo
from aops_utils.restful.status import SUCCEED, PARAM_ERROR

header = {
    "Content-Type": "application/json; charset=UTF-8"
}


class TestConfigManage(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("manager")

        for blue, api in aops_manager.BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    @responses.activate
    @mock.patch.object(UserCache, 'get')
    @mock.patch('aops_manager.config_manager.view.get_host_infos')
    def test_collect_config_should_return_content_when_input_correct(self, mock_host_infos, mock_user):
        req_data = {"infos": [{"host_id": "host_id_test", "config_list": ["test_config_path"]}]}

        resp_data = {"success_files": ["test_config_path"],
                     "fail_files": [],
                     "infos": [{
                         "path": "test_config_path",
                         "file_attr": {
                             "mode": "string",
                             "owner": "string",
                             "group": "string"
                         },
                         "content": "string"
                     }]}
        mock_host_infos.return_value = SUCCEED, {'host_id_test': "localhost"}
        mock_user.return_value = UserInfo('admin', '123', '123456')
        responses.add(responses.POST,
                      'http://localhost/v1/agent/file/collect',
                      json=resp_data,
                      status=200,
                      content_type='application/json'
                      )

        resp = self.client.post('/manage/config/collect', data=json.dumps(req_data), headers=header)
        self.assertEqual(SUCCEED, resp.json.get('code'), resp.text)

    def test_collect_config_should_return_param_error_when_input_incorrect_data(self):
        req_data = {"infos": [{"host_id": 2333, "config_list": ["test_config_path"]}]}
        resp = self.client.post('/manage/config/collect', data=json.dumps(req_data), headers=header)
        self.assertEqual(PARAM_ERROR, json.loads(resp.text).get('code'), resp.text)

    def test_collect_config_should_return_400_when_no_input(self):
        resp = self.client.post('/manage/config/collect', headers=header)
        self.assertEqual(400, resp.status_code, resp.text)

    @mock.patch.object(UserCache, 'get')
    @mock.patch('aops_manager.config_manager.view.get_host_infos')
    def test_collect_config_should_return_fail_list_when_input_host_id_not_in_database(self,
                                                                                       mock_host_infos,
                                                                                       mock_user):
        req_data = {"infos": [{"host_id": "host_id_test", "config_list": ["test_config_path"]}]}

        mock_host_infos.return_value = SUCCEED, {}
        mock_user.return_value = UserInfo('admin', '123', '123456')
        resp = self.client.post('/manage/config/collect', data=json.dumps(req_data), headers=header)
        self.assertEqual(["test_config_path"], json.loads(resp.text).get('resp')[0].get('fail_files'), resp.text)

    @mock.patch.object(UserCache, 'get')
    @mock.patch('aops_manager.config_manager.view.requests.post')
    @mock.patch('aops_manager.config_manager.view.get_host_infos')
    def test_collect_config_should_return_fail_list_when_agent_server_is_not_running(self,
                                                                                     mock_host_infos,
                                                                                     mock_requests_post, mock_user):
        req_data = {"infos": [{"host_id": "host_id_test", "config_list": ["test_config_path"]}]}

        mock_host_infos.return_value = SUCCEED, {'host_id_test': "localhost"}
        mock_requests_post.side_effect = requests.exceptions.ConnectionError()
        mock_user.return_value = UserInfo('admin', '123', '123456')
        resp = self.client.post('/manage/config/collect', data=json.dumps(req_data), headers=header)
        self.assertEqual(["test_config_path"], json.loads(resp.text).get('resp')[0].get('fail_files'), resp.text)

    @responses.activate
    @mock.patch.object(UserCache, 'get')
    @mock.patch('aops_manager.config_manager.view.get_host_infos')
    def test_collect_config_should_return_succeed_host_id_and_fail_host_id_when_part_of_the_input_host_id_is_wrong(
            self, mock_host_infos, mock_user):
        """
            You should see that the host_id_test1 can get content and the host_id_test1 can't get content.
        """
        req_data = {"infos": [{"host_id": "host_id_test1", "config_list": ["test_config_path"]},
                              {"host_id": "host_id_test2", "config_list": ["test_config_path"]}]}
        mock_host_infos.return_value = SUCCEED, {'host_id_test1': "localhost"}
        mock_user.return_value = UserInfo('admin', '123', '123456')
        resp_data = {"success_files": ["test_config_path"],
                     "fail_files": [],
                     "infos": [{
                         "path": "test_config_path",
                         "file_attr": {"mode": "string", "owner": "string", "group": "string"},
                         "content": "string"
                     }]}

        expected_result = [{"host_id": "host_id_test1",
                            "success_files": ["test_config_path"],
                            "fail_files": [],
                            "infos": [{"path": "test_config_path",
                                       "file_attr": {"mode": "string", "owner": "string", "group": "string"},
                                       "content": "string"}]
                            },
                           {"host_id": "host_id_test2",
                            "success_files": [],
                            "fail_files": ["test_config_path"],
                            "content": {}}]

        responses.add(responses.POST,
                      'http://localhost/v1/agent/file/collect',
                      json=resp_data,
                      status=200,
                      content_type='application/json'
                      )
        resp = self.client.post('/manage/config/collect', data=json.dumps(req_data), headers=header)
        self.assertEqual(expected_result, json.loads(resp.text).get('resp'), resp.text)
