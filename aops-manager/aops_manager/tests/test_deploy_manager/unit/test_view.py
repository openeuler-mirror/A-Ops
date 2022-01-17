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
Time: 2022-01-10 10:43:53
Author: peixiaochao
Description:
"""
import unittest
from unittest import mock
from flask import Flask

import aops_manager
from aops_utils.restful.status import StatusCode, PARAM_ERROR, SUCCEED
from aops_utils.conf.constant import GENERATE_TASK, DELETE_TASK, GET_TASK, IMPORT_TEMPLATE, \
    DELETE_TEMPLATE, GET_TEMPLATE
from aops_utils.compare import compare_two_object
from aops_utils.restful.response import MyResponse
from aops_utils.restful.resource import BaseResource

app = Flask("manager")
for blue, api in aops_manager.BLUE_POINT:
    api.init_app(blue)
    app.register_blueprint(blue)
app.testing = True
client = app.test_client()
header = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "81fe"
}


class TestDeployManage(unittest.TestCase):
    """
    test deploy manager restful
    """

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_add_task(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED
        # normal
        args = {
            "task_name": "name1",
            "description": "xx",
            "template_name": ["t1", "t2"]
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200
            mock_operate.return_value = expected_res
            client.post(GENERATE_TASK, json=args, headers=header)
            self.assertIn('task_id', mock_operate.call_args[0][1].keys())

        # abnormal, miss param
        args = {
            "task_name": "a"
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.post(GENERATE_TASK, json=args, headers=header)
        self.assertTrue(compare_two_object(response.json, expected_res))

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_delete_task(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED

        # normal
        args = {
            "task_list": ["name1", "name2"]
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200
            mock_operate.return_value = expected_res
            client.delete(DELETE_TASK, json=args, headers=header)
            self.assertEqual(args, mock_operate.call_args[0][1])

        # abnormal, wrong format
        args = {
            "task_list": 'a'
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.delete(DELETE_TASK, json=args, headers=header)
        args['username'] = 'admin'
        self.assertTrue(compare_two_object(response.json, expected_res))

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_get_task(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED
        # normal
        args = {
            "task_list": ["name1", "name2"]
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200
            mock_operate.return_value = expected_res
            client.post(GET_TASK, json=args, headers=header)
            self.assertEqual(args, mock_operate.call_args[0][1])

        # abnormal, wrong param
        args = {
            "task_list": ["a"],
            "sssa": 1
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.post(GET_TASK, json=args, headers=header)
        res = response.json
        self.assertTrue(compare_two_object(res, expected_res))

        # ==============execute task===================

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_import_template(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED

        # normal
        args = {
            "template_name": "aa",
            "template_content": {},
            "description": "xx"
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200
            mock_operate.return_value = expected_res
            client.post(IMPORT_TEMPLATE, json=args, headers=header)
            self.assertEqual(args, mock_operate.call_args[0][1])

        # abnormal, miss param
        args = {
            "task_name": "a"
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.post(IMPORT_TEMPLATE, json=args, headers=header)
        self.assertTrue(compare_two_object(response.json, expected_res))

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_get_template(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED
        # normal
        args = {
            "template_list": ["xx"]
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200

            mock_operate.return_value = expected_res
            client.post(GET_TEMPLATE, json=args, headers=header)
            self.assertEqual(args, mock_operate.call_args[0][1])

        # abnormal, wrong param format
        args = {
            "template_list": [1, 2]
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.post(GET_TEMPLATE, json=args, headers=header)
        res = response.json
        self.assertTrue(compare_two_object(res, expected_res))

    @mock.patch.object(MyResponse, "verify_token")
    def test_restful_manage_delete_template(self, mock_verify_token):
        mock_verify_token.return_value = SUCCEED

        # normal
        args = {
            "template_list": ["x"]
        }
        with mock.patch.object(BaseResource, "operate") as mock_operate:
            expected_res = 200
            mock_operate.return_value = expected_res
            client.delete(DELETE_TEMPLATE, json=args, headers=header)
            self.assertEqual(args, mock_operate.call_args[0][1])

        # abnormal, wrong param
        args = {
            "task_name": "a"
        }
        expected_res = StatusCode.make_response(PARAM_ERROR)
        response = client.delete(DELETE_TEMPLATE, json=args)
        res = response.json
        self.assertTrue(compare_two_object(res, expected_res))
