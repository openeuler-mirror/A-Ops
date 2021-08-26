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
from flask import Flask

import aops_database
from aops_utils.conf.constant import DATA_ADD_TASK, DATA_ADD_TEMPLATE, DATA_DELETE_TASK, DATA_GET_TASK, DATA_GET_TEMPLATE, DATA_DELETE_TEMPLATE
from aops_utils.restful.status import SUCCEED, StatusCode


class TestDeployData(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("database")

        for blue, api in aops_database.BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()
        self.succeed_res = StatusCode.make_response(SUCCEED)

    def test_restful_data_template(self):
        args = {
            "test": 1
        }
        # ==============add template===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_ADD_TEMPLATE, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'add_template')

        # ==============delete template===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED

            response = self.client.delete(DATA_DELETE_TEMPLATE, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'delete_template')
        
        # ==============get template===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_GET_TEMPLATE, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_template')
        

        # ==============add task ===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_ADD_TASK, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'add_task')

        # ==============delete task ===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.delete(DATA_DELETE_TASK, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'delete_task')

        # ==============get task ===================
        with mock.patch("aops_database.views.deploy.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_GET_TASK, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_task')
