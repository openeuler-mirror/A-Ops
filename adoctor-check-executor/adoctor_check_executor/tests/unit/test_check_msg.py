#!/usr/bin/python3
# -*- coding:UTF=8 -*-
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
Author: YangYunYi
Date: 2021/9/1 20:11
docs: test_check_msg.py
description: test check msg
"""

import unittest
from unittest import mock
from adoctor_check_executor.common.check_msg import CheckMsgToolKit
from adoctor_check_executor.check_executor.check_item import CheckItemDetail


class TestCheckMsgToolKil(unittest.TestCase):
    def test_build_abnormal_data(self):
        check_item_config = {
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            },
                {
                    "name": "data_item2",
                    "label": {
                        "cpu": "1"
                    }
                }
            ],
            "condition": "data_item1>1",
            "plugin": "",
            "description": "aaa"
        }
        check_item_detail = CheckItemDetail("admin", check_item_config)
        abnormal_data = {
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            },
                {
                    "name": "data_item2",
                    "label": {
                        "cpu": "1"
                    }
                }
            ],
            "condition": "data_item1>1",
            "plugin": 'expression_rule_plugin',
            "description": "aaa",
            "host_id": "1111",
            "start": 11111,
            "end": 22222,
            "value": "No data",
            "username": "admin"
        }
        ret = CheckMsgToolKit.build_abnormal_data(check_item_detail,
                                                  [11111, 22222], "1111", "No data")
        self.assertDictEqual(abnormal_data, ret)

    @mock.patch("adoctor_check_executor.common.check_msg.MyResponse")
    @mock.patch("adoctor_check_executor.common.check_msg.make_datacenter_url")
    def test_save_check_result_to_database(self, mock_make_url, mock_myresponse):
        abnormal_data_list = [{
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            },
                {
                    "name": "data_item2",
                    "label": {
                        "cpu": "1"
                    }
                }
            ],
            "condition": "data_item1>1",
            "plugin": 'expression_rule_plugin',
            "description": "aaa",
            "host_id": "1111",
            "start": 11111,
            "end": 22222,
            "value": "No data",
            "username": "admin"
        }]
        response = {"code": 200, "msg": "operation succeed"}
        mock_myresponse.get_result.return_value = response
        mock_make_url.return_value = "http://101.1.1.1:1111"
        self.assertDictEqual(CheckMsgToolKit.save_check_result_to_database(abnormal_data_list),
                             response)

    @mock.patch("adoctor_check_executor.common.check_msg.MyResponse")
    @mock.patch("adoctor_check_executor.common.check_msg.make_datacenter_url")
    def test_delete_check_result_from_database(self, mock_make_url, mock_myresponse):
        host_list = ["11111", "222222"]
        time_range = [12222, 122223]
        check_items = ["check_item1",  "check_item2"]

        response = {"code": 200, "msg": "operation succeed"}
        mock_myresponse.get_result.return_value = response
        mock_make_url.return_value = "http://101.1.1.1:1111"
        self.assertDictEqual(CheckMsgToolKit.delete_check_result_from_database(host_list,
                                                                               time_range,
                                                                               "admin",
                                                                               check_items),
                             response)


    @mock.patch("adoctor_check_executor.common.check_msg.MyResponse")
    @mock.patch("adoctor_check_executor.common.check_msg.make_datacenter_url")
    def test_get_data_from_database(self, mock_make_url, mock_myresponse):
        data_list = [{
            "name": "node_cpu_seconds_total",
            "label": {'cpu': '1', 'mode': 'irq'}
        },
            {
                "name": "node_context_switches_total",
                "label": {
                }
            }
        ]
        response = {'code': 200, 'fail_list': [], 'msg': 'openration succeed',
                    'succeed_list': [
                        {'host_id': '90.90.64.65', 'label': {'cpu': '1', 'mode': 'irq'},
                         'name': 'node_cpu_seconds_total',
                         'values': [[1630422037.931, '337.64'], [1630422052.931, '337.64'],
                                    [1630422067.931, '337.64'], [1630422082.931, '337.64'],
                                    [1630422097.931, '337.64'], [1630422112.931, '337.65']]},
                        {'host_id': '90.90.64.65', 'label': {},
                         'name': 'node_context_switches_total',
                         'values': [[1630422037.931, '3564846944'], [1630422052.931, '3564880397'],
                                    [1630422067.931, '3564917043'], [1630422082.931, '3564949919'],
                                    [1630422097.931, '3564986484'],
                                    [1630422112.931, '3565020103']]}]}
        mock_myresponse.get_result.return_value = response
        mock_make_url.return_value = "http://101.1.1.1:1111"
        self.assertDictEqual(CheckMsgToolKit.get_data_from_database([1630422037, 1630422113],
                                                                    '90.90.64.65', data_list),
                             response)

    @mock.patch("adoctor_check_executor.common.check_msg.MyResponse")
    @mock.patch("adoctor_check_executor.common.check_msg.make_datacenter_url")
    def test_get_check_rule_from_database(self, mock_make_url, mock_myresponse):
        check_items = [{
            "check_item": "check_item1",
            "data_list": [{
                "name": "node_cpu_seconds_total",
                "type": "kpi",
                "label": {
                    "cpu": "1",
                    "mode": "irq"
                }
            }],
            "condition": "$0>1",
            "plugin": "",
            "description": "aaa"
        }]
        response = {'code': 200, 'msg': 'openration succeed', "check_items": check_items}
        mock_myresponse.get_result.return_value = response
        mock_make_url.return_value = "http://101.1.1.1:1111"
        self.assertListEqual(CheckMsgToolKit.get_check_rule_from_database("admin"),
                             check_items)

    @mock.patch("adoctor_check_executor.common.check_msg.MyResponse")
    @mock.patch("adoctor_check_executor.common.check_msg.make_datacenter_url")
    def test_get_user_list_from_database(self, mock_make_url, mock_myresponse):
        response = {'code': 200, 'host_infos': {'admin': [
            {'host_group_name': 'group1',
             'host_id': 'eca3b022070211ecab3ca01c8d75c8f3', 'host_name': '90.90.64.65',
             'public_ip': '90.90.64.65', 'ssh_port': 22},
            {'host_group_name': 'group1',
             'host_id': 'f485bd26070211ecaa06a01c8d75c8f3', 'host_name': '90.90.64.64',
             'public_ip': '90.90.64.64', 'ssh_port': 22},
            {'host_group_name': 'group1',
             'host_id': 'fa05c1ba070211ecad52a01c8d75c8f3', 'host_name': '90.90.64.66',
             'public_ip': '90.90.64.66', 'ssh_port': 22}]}, 'msg': 'openration succeed'}
        mock_myresponse.get_result.return_value = response
        mock_make_url.return_value = "http://101.1.1.1:1111"
        self.assertListEqual(CheckMsgToolKit.get_user_list_from_database(),
                             ["admin"])
