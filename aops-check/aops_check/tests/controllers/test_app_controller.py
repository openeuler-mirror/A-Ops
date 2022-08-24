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
"""
Time:
Author:
Description:
"""
import unittest
from unittest import mock
from flask import Flask
from flask_restful import Api
from flask.blueprints import Blueprint

from aops_utils.restful.status import PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR, SUCCEED

import aops_check
from aops_check.conf.constant import CREATE_APP, QUERY_APP, QUERY_APP_LIST
from aops_check.url import SPECIFIC_URLS

API = Api()
for view, url in SPECIFIC_URLS['APP_URLS']:
    API.add_resource(view, url)

CHECK = Blueprint('check', __name__)
app = Flask("check")
API.init_app(CHECK)
app.register_blueprint(CHECK)

app.testing = True
client = app.test_client()
header = {
    "Content-Type": "application/json; charset=UTF-8"
}
header_with_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "81fe"
}


class AppControllerTestCase(unittest.TestCase):
    """
    AppController integration tests stubs
    """

    def test_create_app_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.get(CREATE_APP, json=args).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_create_app_should_return_param_error_when_input_wrong_param(self):
        args = {
            "app_name": "app1",
            "description": "",
            "api": {
                "type": 1,
                "address1": "sx"
            }
        }
        response = client.post(CREATE_APP, json=args,
                               headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_create_app_should_return_token_error_when_input_wrong_token(self):
        args = {
            "app_name": "app1",
            "description": "xx",
            "api": {
                "type": "api",
                "address": "execute"
            },
            "detail": {}
        }
        response = client.post(CREATE_APP, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_create_app_should_return_database_error_when_database_is_wrong(self):
        args = {
            "app_name": "app1",
            "description": "xx",
            "api": {
                "type": "api",
                "address": "execute"
            },
            "detail": {}
        }
        with mock.patch("aops_check.controllers.app_controller.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.post(CREATE_APP, json=args,
                                   headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_create_app_should_return_app_id_when_correct(self):
        args = {
            "app_name": "app1",
            "description": "xx",
            "api": {
                "type": "api",
                "address": "execute"
            },
            "detail": {}
        }
        with mock.patch("aops_check.controllers.app_controller.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.post(CREATE_APP, json=args,
                                   headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)
            self.assertIn('app_id', response.keys())

    def test_query_app_list_should_return_error_when_request_method_is_wrong(self):
        response = client.post(QUERY_APP_LIST).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_query_app_list_should_return_param_error_when_input_wrong_param(self):
        response = client.get(
            QUERY_APP_LIST + "?page=1&per_page='1'", headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_query_app_list_should_return_token_error_when_input_wrong_token(self):
        response = client.get(
            QUERY_APP_LIST + "?page=1&per_page=2", headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_query_app_list_should_return_database_error_when_database_is_wrong(self):
        with mock.patch("aops_utils.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.get(
                QUERY_APP_LIST + "?page=1&per_page=2", headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_query_app_list_should_return_succeed_when_correct(self):
        with mock.patch("aops_utils.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.get(
                QUERY_APP_LIST + "?page=1&per_page=2", headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)

    def test_query_app_should_return_error_when_request_method_is_wrong(self):
        response = client.post(QUERY_APP).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_query_app_should_return_param_error_when_input_wrong_param(self):
        response = client.get(QUERY_APP + "?app=1",
                              headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_query_app_should_return_token_error_when_input_wrong_token(self):
        response = client.get(QUERY_APP + "?app_id='1'", headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_query_app_should_return_database_error_when_database_is_wrong(self):
        with mock.patch("aops_utils.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.get(QUERY_APP + "?app_id='2'",
                                  headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_query_app_should_return_succeed_when_correct(self):
        with mock.patch("aops_utils.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.get(QUERY_APP + "?app_id='3'",
                                  headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)


if __name__ == '__main__':
    import unittest

    unittest.main()
