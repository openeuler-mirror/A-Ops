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
import os
import unittest
from unittest import mock
from flask import Flask
import requests
import json

import aops_manager
from aops_manager.config_manager import view
from aops_utils.restful.status import StatusCode
from aops_utils.conf.constant import COLLECT_CONFIG
from aops_utils.restful.response import MyResponse
from aops_manager.account_manager.key import HostKey
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder


class TestConfigManage(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("manager")

        for blue, api in aops_manager.BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    @mock.patch.object(HostKey, "key")
    @mock.patch.object(MyResponse, "get_response")
    def test_restful_manage_read_config(self, mock_response, mock_key):
        # normal
        data = {
            "infos": [
                {
                    "host_id": "f93485c4fe9111ebade53e22fbb33802",
                    "config_list": ["/etc/hostname", "/etc/yum.repos.d/openEuler.repo"]
                },
                {
                    "host_id": "f9348f9cfe9111ebade53e22fbb33802",
                    "config_list": ["/etc/hostname"]
                }
            ]
        }
        mock_response.side_effect = [
            {
                "code": 200,
                "msg": 'openration succeed',
                "host_infos": [
                    {
                        "host_id": "f93485c4fe9111ebade53e22fbb33802",
                        "host_name": "host1",
                        "public_ip": "90.90.64.64",
                    },
                    {
                        "host_id": "f93485c4fe9111ebade53e22fbb33802",
                        "host_name": "host2",
                        "public_ip": "90.90.64.65"
                    }
                ]
            }
        ]
        mock_key.return_value = "miyao"
        with mock.patch.object(view, "inventory_operate") as mock_inventory:
            mock_inventory.return_value = True
            with mock.patch.object(InventoryBuilder, "move_host_vars_to_inventory") as host_vars:
                host_vars.return_value = True
                with mock.patch.object(view, "generate_output") as mock_out:
                    mock_out.return_value = [], [], \
                                            [{"host1": "shot"}], False
                self.client.get(COLLECT_CONFIG, json=data)
                print(mock_response.call_args_list)
                for i in range(len(data['infos'])):
                    self.assertEqual(data['infos'][i]['host_id'],
                                     mock_response.call_args_list[0][0][2]['host_list'][i])
