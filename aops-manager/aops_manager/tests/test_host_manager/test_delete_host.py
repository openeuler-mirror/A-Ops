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
from unittest import mock

from flask import Flask
import responses

from aops_manager import BLUE_POINT
from aops_manager.database.proxy.host import HostProxy
from aops_utils.restful.status import SUCCEED, TOKEN_ERROR, DATABASE_CONNECT_ERROR

app = Flask("check")
for blue, api in BLUE_POINT:
    api.init_app(blue)
    app.register_blueprint(blue)

app.testing = True
client = app.test_client()
header = {
    "Content-Type": "application/json; charset=UTF-8"
}
header_with_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "123456"
}


class TestDeleteHost(unittest.TestCase):
    @responses.activate
    @mock.patch.object(HostProxy, 'delete_host')
    @mock.patch.object(HostProxy, 'connect')
    def test_delete_host_should_return_success_list_when_input_host_id_is_in_database_and_not_in_workflow(
            self, mock_mysql_connect, mock_delete_host):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        mock_mysql_connect.return_value = True
        mock_delete_host.return_value = SUCCEED, {
            'succeed_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3'],
            'fail_list': [],
            'host_info': {'test_host_id_1': '', 'test_host_id_2': '', 'test_host_id_3': ''}
        }
        mock_check_json = {
            'code': 200,
            'msg': 'xxxxx',
            'result': {host_id: False for host_id in input_data['host_list']}
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11112/check/workflow/host/exist',
                      json=mock_check_json,
                      status=200,
                      content_type='application/json'
                      )
        resp = client.delete('/manage/host/delete', json=input_data, headers=header_with_token)
        self.assertEqual(input_data['host_list'], resp.json['succeed_list'])

    @responses.activate
    @mock.patch.object(HostProxy, 'delete_host')
    @mock.patch.object(HostProxy, 'connect')
    def test_delete_host_should_return_fail_list_when_input_host_id_is_in_database_and_workflow(
            self, mock_mysql_connect, mock_delete_host):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        mock_mysql_connect.return_value = True
        mock_delete_host.return_value = SUCCEED, {
            'succeed_list': [],
            'fail_list': [],
            'host_info': {}
        }
        mock_check_json = {
            'code': 200,
            'msg': 'xxxxx',
            'result': {host_id: True for host_id in input_data['host_list']}
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11112/check/workflow/host/exist',
                      json=mock_check_json,
                      status=200,
                      content_type='application/json'
                      )
        resp = client.delete('/manage/host/delete', json=input_data, headers=header_with_token)
        self.assertEqual(input_data['host_list'], resp.json['fail_list'])

    @responses.activate
    @mock.patch.object(HostProxy, 'delete_host')
    @mock.patch.object(HostProxy, 'connect')
    def test_delete_host_should_return_succeed_list_and_fail_list_when_part_of_input_host_id_is_in_database_and_workflow(
            self, mock_mysql_connect, mock_delete_host):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        mock_mysql_connect.return_value = True
        mock_delete_host.return_value = SUCCEED, {
            'succeed_list': ['test_host_id_2'],
            'fail_list': [],
            'host_info': {'test_host_id_2': ''}
        }
        mock_check_json = {
            'code': 200,
            'msg': 'xxxxx',
            'result': {'test_host_id_1': True, 'test_host_id_2': False, 'test_host_id_3': True}
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11112/check/workflow/host/exist',
                      json=mock_check_json,
                      status=200,
                      content_type='application/json'
                      )
        resp = client.delete('/manage/host/delete', json=input_data, headers=header_with_token)
        expect_fail_list = ['test_host_id_1', 'test_host_id_3']
        self.assertEqual(expect_fail_list, resp.json.get('fail_list'), resp.json)

    def test_delete_host_should_return_token_error_when_part_of_input_with_no_token(self):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        resp = client.delete('/manage/host/delete', json=input_data, headers=header)

        self.assertEqual(TOKEN_ERROR, resp.json.get('code'), resp.json)

    def test_delete_host_should_return_400_when_no_input(self):
        resp = client.delete('/manage/host/delete', headers=header_with_token)
        self.assertEqual(400, resp.status_code, resp.json)

    @responses.activate
    @mock.patch.object(HostProxy, 'connect')
    def test_delete_host_should_return_fail_list_when_aops_check_cannot_be_accessed(
            self, mock_mysql_connect):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        mock_mysql_connect.return_value = True
        responses.add(responses.POST,
                      'http://127.0.0.1:11112/check/workflow/host/exist',
                      json={'code': 500, 'msg': 'xxxxxxxx'},
                      status=500,
                      content_type='application/json'
                      )
        resp = client.delete('/manage/host/delete', json=input_data, headers=header_with_token)
        self.assertEqual(input_data['host_list'], resp.json.get('fail_list'), resp.json)

    @mock.patch.object(HostProxy, 'connect')
    def test_delete_host_should_return_database_error_when_database_cannot_connect(
            self, mock_mysql_connect):
        input_data = {'host_list': ['test_host_id_1', 'test_host_id_2', 'test_host_id_3']}
        mock_mysql_connect.return_value = False
        resp = client.delete('/manage/host/delete', json=input_data, headers=header_with_token)
        self.assertEqual(DATABASE_CONNECT_ERROR, resp.json.get('code'), resp.json)
