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
from aops_utils.conf.constant import DATA_ADD_HOST, DATA_DELETE_HOST, DATA_GET_HOST, DATA_ADD_GROUP, DATA_DELETE_GROUP, DATA_GET_GROUP, DATA_GET_HOST_COUNT, DATA_GET_HOST_INFO_BY_USER, DATA_SAVE_HOST_INFO, DATA_GET_HOST_INFO, DATA_DELETE_HOST_INFO
from aops_utils.restful.status import SUCCEED, StatusCode
from aops_database.proxy.host import HostDatabase, HostInfoDatabase


class TestHostData(unittest.TestCase):
    def setUp(self):
        app = Flask("database")

        for blue, api in aops_database.BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

        self.succeed_res = StatusCode.make_response(SUCCEED)

    def test_restful_data_host(self):
        args = {
            "test": 1
        }
        # ==============add host===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_ADD_HOST, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'add_host')

        # ==============delete host===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED

            response = self.client.delete(DATA_DELETE_HOST, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'delete_host')
        
        # ==============get host===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.get(DATA_GET_HOST, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_host')
        
        # ==============get host count===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.get(DATA_GET_HOST_COUNT, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_host_count')

        # ==============add host group===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_ADD_GROUP, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'add_host_group')

        # ==============delete host group===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.delete(DATA_DELETE_GROUP, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'delete_host_group')

        # ==============get host group===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.get(DATA_GET_GROUP, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_host_group')

        # ==============get host info===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            args = {
                "basic": True
            }
            response = self.client.get(DATA_GET_HOST_INFO, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertTrue(isinstance(mock_operate.call_args_list[0][0][0], HostDatabase))
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_host_info')
        
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            args = {
            }
            response = self.client.get(DATA_GET_HOST_INFO, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertTrue(isinstance(mock_operate.call_args_list[0][0][0], HostInfoDatabase))
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_host_info')

        # ==============get host info by user===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.get(DATA_GET_HOST_INFO_BY_USER, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'get_total_host_info_by_user')

        # ==============save host info===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(DATA_SAVE_HOST_INFO, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'save_host_info')

        # ==============delete host info===================
        with mock.patch("aops_database.views.host.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.delete(DATA_DELETE_HOST_INFO, json=args)
            res = response.json
            self.assertEqual(res, self.succeed_res)
            self.assertEqual(mock_operate.call_args_list[0][0][1], args)
            self.assertEqual(mock_operate.call_args_list[0][0][2], 'delete_host_info')