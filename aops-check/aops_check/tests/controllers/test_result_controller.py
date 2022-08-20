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
from sqlalchemy.orm import scoping

import aops_check
from aops_utils.restful.status import PARAM_ERROR, TOKEN_ERROR, SUCCEED
from aops_check.database.dao.result_dao import ResultDao

app = Flask("check")
for blue, api in aops_check.BLUE_POINT:
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


class TestResultController(unittest.TestCase):

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_check_result_result_when_input_correct_alert_id(
            self, mock_session, mock_connect, mock_query_result_host):
        mock_result = {
            "result": {
                "sasda": {
                    "host_ip": "hsadghaj",
                    "host_name": "adhj",
                    "is_root": True,
                    "host_check_result": [
                        {
                            "sasda": {
                                "is_root": False,
                                "label": "hadjhsjk",
                                "metric_name": "adsda",
                                "time": 20180106
                            }
                        },
                        {
                            "sasda": {
                                "is_root": True,
                                "label": "assda",
                                "metric_name": "1231",
                                "time": 3
                            }
                        }
                    ]
                }
            }
        }
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = 'test'
        resp = client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(mock_result, resp.json.get('result'))

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_empty_result_when_input_incorrect_alert_id(
            self, mock_session, mock_connect, mock_query_result_host):
        mock_result = {"result": {}}
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = 'test'
        resp = client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(mock_result, resp.json.get('result'))

    def test_get_host_result_should_param_error_result_when_no_input(
            self, ):
        resp = client.get(f'/check/result/host', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('code'))

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_param_error_when_input_alert_id_is_null(
            self, mock_session, mock_connect, mock_query_result_host):
        mock_result = {"result": {}}
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = ''
        resp = client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('code'))

    def test_get_host_result_should_return_token_error_when_input_with_no_token(self):
        mock_alert_id = 'test'
        resp = client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('code'))

    def test_get_host_result_should_return_405_when_request_by_other_method(self):
        mock_alert_id = 'test'
        resp = client.post(f'/check/result/host?alert_id={mock_alert_id}',
                           headers=header_with_token)
        self.assertEqual(405, resp.status_code)
