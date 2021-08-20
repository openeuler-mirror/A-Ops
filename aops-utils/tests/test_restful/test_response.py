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
import requests
import unittest
from unittest import mock

from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import HTTP_CONNECT_ERROR, PARAM_ERROR, SUCCEED, StatusCode


class TestResponse(unittest.TestCase):
    def test_restful_get_response(self):
        method = "get"
        url = "http://1"
        data = [1]
        res = MyResponse.get_response(method, url, data)
        expected_res = StatusCode.make_response(PARAM_ERROR)
        self.assertEqual(res, expected_res)

        data = {
                "a": 1
            }
        header = {
                "access_token": "b"
            }
        with mock.patch.object(requests, "request") as mock_request:
            res = MyResponse.get_response(method, url, data, header)
            mock_request.assert_called_once
        
        res = MyResponse.get_response(method, url, data)
        expected_res = StatusCode.make_response(HTTP_CONNECT_ERROR)
        self.assertEqual(res, expected_res)
    
    def test_restful_verify_args(self):
        with mock.patch("aops_utils.restful.response.validate") as mock_validate:
            mock_validate.return_value = (1, 2)
            res = MyResponse.verify_args(1, 1)
            self.assertEqual(res, PARAM_ERROR)

    def test_restful_verify_all(self):
        with mock.patch.object(MyResponse, 'verify_args') as mock_args:
            mock_args.side_effect = [1, SUCCEED]
            res = MyResponse.verify_all(1,2,1)
            self.assertEqual(res, 1)

            with mock.patch.object(MyResponse, 'verify_token') as mock_token:
                mock_token.return_value = 5
                res = MyResponse.verify_all(1,2,1)
                self.assertEqual(res, 5)
    
    def test_restful_get_result(self):
        with mock.patch.object(MyResponse, "get_response") as mock_response:
            MyResponse.get_result(SUCCEED, 1,1,1)
            mock_response.assert_called_once
        
        res = MyResponse.get_result(PARAM_ERROR, 1,1,1)
        expected_res = StatusCode.make_response(PARAM_ERROR)
        self.assertEqual(res, expected_res)