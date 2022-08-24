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
from urllib.parse import urlencode

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

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_correct(self,
                                                                            mock_sort,
                                                                            mock_session,
                                                                            mock_count,
                                                                            mock_connect,
                                                                            mock_query_from_database,
                                                                            mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'level': 'test',
            'confirmed': 'true',
            'sort': 'time',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test",
            "time": 20201111,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_page(self,
                                                                                 mock_sort,
                                                                                 mock_session,
                                                                                 mock_count,
                                                                                 mock_connect,
                                                                                 mock_query_from_database,
                                                                                 mock_rows_to_list):
        mock_param = {
            'per_page': '5',
            'domain': 'test',
            'level': 'test',
            'confirmed': 'true',
            'sort': 'time',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test",
            "time": 20201111,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_perpage(self,
                                                                                    mock_sort,
                                                                                    mock_session,
                                                                                    mock_count,
                                                                                    mock_connect,
                                                                                    mock_query_from_database,
                                                                                    mock_rows_to_list):
        mock_param = {
            'page': '1',
            'domain': 'test',
            'level': 'test',
            'confirmed': 'true',
            'sort': 'time',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test",
            "time": 20201111,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_domain(self,
                                                                                   mock_sort,
                                                                                   mock_session,
                                                                                   mock_count,
                                                                                   mock_connect,
                                                                                   mock_query_from_database,
                                                                                   mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'level': 'test',
            'confirmed': 'true',
            'sort': 'time',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test1",
            "host_num": 1,
            "level": "test",
            "time": 20201111,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test2",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_level(self,
                                                                                  mock_sort,
                                                                                  mock_session,
                                                                                  mock_count,
                                                                                  mock_connect,
                                                                                  mock_query_from_database,
                                                                                  mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'confirmed': 'true',
            'sort': 'time',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test1",
            "time": 20201111,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_sort(self,
                                                                                 mock_sort,
                                                                                 mock_session,
                                                                                 mock_count,
                                                                                 mock_connect,
                                                                                 mock_query_from_database,
                                                                                 mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'confirmed': 'true',
            'level': 'test',
            'direction': 'desc'
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test1",
            "time": 20180102,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_direction(self,
                                                                                      mock_sort,
                                                                                      mock_session,
                                                                                      mock_count,
                                                                                      mock_connect,
                                                                                      mock_query_from_database,
                                                                                      mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'confirmed': 'true',
            'level': 'test',
            'sort': 'time',
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test1",
            "time": 20180102,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('aops_check.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_direction(self,
                                                                                      mock_sort,
                                                                                      mock_session,
                                                                                      mock_count,
                                                                                      mock_connect,
                                                                                      mock_query_from_database,
                                                                                      mock_rows_to_list):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'confirmed': 'true',
            'level': 'test',
            'sort': 'time',
        }

        check_result_list = [{
            "alert_id": "alert_1",
            "alert_name": "test",
            "confirmed": 1,
            "domain": "test",
            "host_num": 1,
            "level": "test1",
            "time": 20180102,
            "workflow_id": "workflow_id_1",
            "workflow_name": "workflow_name_1"
        },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": 1,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2"
            }]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    def test_query_result_list_should_return_token_error_when_input_with_no_token(self):
        mock_param = {}
        resp = client.get('/check/result/list', data=mock_param, headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('code'))

    def test_query_result_list_should_return_405_when_input_with_request_by_other_method(self):
        mock_param = {}
        resp = client.post('/check/result/list', data=mock_param, headers=header_with_token)
        self.assertEqual(405, resp.status_code)

    def test_query_result_list_should_return_param_error_when_input_with_request_input_error_info(self):
        mock_param = {"test": "test"}
        resp = client.get(f'/check/result/list?test={mock_param["test"]}', data=mock_param,
                          headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('code'))
