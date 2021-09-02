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
Date: 2021/8/28 11:40
docs: test_data_manager.py
description: test data manager
"""

import unittest
from unittest import mock
from adoctor_check_executor.check_executor.data_manager import DataManager
from adoctor_check_executor.check_executor.check_item import CheckItemDetail


class TestDataManager(unittest.TestCase):

    def setUp(self) -> None:
        self.data_list = [{
            "name": "node_cpu_frequency_hertz",
            "type": "kpi",
            "label": {
                "cpu": "1"
            }
        },
            {
                "name": "go_memstats_sys_bytes",
                "type": "log",
                "label": {
                    "cpu": "1",
                    "mode": "irq"

                }
            },
            {
                "name": "node_boot_time_seconds",
                "type": "kpi"
            }]

        self.host_list = [{"host_id": "11111", "public_ip": "90.90.64.65"},
                          {"host_id": "22222", "public_ip": "90.90.64.64"},
                          {"host_id": "33333", "public_ip": "90.90.64.66"}]

        self.host_cache = {'90.90.64.65': {
            '$0': [[1630120927.931, '1627981323'], [1630120942.931, '1627981323'],
                   [1630120957.931, '1627981323'], [1630120972.931, '1627981323'],
                   [1630120987.931, '1627981323'], [1630121002.931, '1627981323'],
                   [1630121017.931, '1627981323'], [1630121032.931, '1627981323'],
                   [1630121047.931, '1627981323'], [1630121062.931, '1627981323'],
                   [1630121077.931, '1627981323'], [1630121092.931, '1627981323'],
                   [1630121107.931, '1627981323'], [1630121122.931, '1627981323'],
                   [1630121137.931, '1627981323'], [1630121152.931, '1627981323'],
                   [1630121167.931, '1627981323'], [1630121182.931, '1627981323'],
                   [1630121197.931, '1627981323']]},
            '90.90.64.64': {
                '$0': [[1630120931.143, '1627527809'], [1630120946.143, '1627527809'],
                       [1630120961.143, '1627527809'], [1630120976.143, '1627527809'],
                       [1630120991.143, '1627527809'], [1630121006.143, '1627527809'],
                       [1630121021.143, '1627527809'], [1630121036.143, '1627527809'],
                       [1630121051.143, '1627527809'], [1630121066.143, '1627527809'],
                       [1630121081.143, '1627527809'], [1630121096.143, '1627527809'],
                       [1630121111.143, '1627527809'], [1630121126.143, '1627527809'],
                       [1630121141.143, '1627527809'], [1630121156.143, '1627527809'],
                       [1630121171.143, '1627527809'], [1630121186.143, '1627527809']]},
            '90.90.64.66': {
                '$0': [[1630120922.999, '1627345015'], [1630120937.999, '1627345015'],
                       [1630120952.999, '1627345015'], [1630120967.999, '1627345015'],
                       [1630120982.999, '1627345015'], [1630120997.999, '1627345015'],
                       [1630121012.999, '1627345015'], [1630121027.999, '1627345015'],
                       [1630121042.999, '1627345015'], [1630121057.999, '1627345015'],
                       [1630121072.999, '1627345015'], [1630121087.999, '1627345015'],
                       [1630121102.999, '1627345015'], [1630121117.999, '1627345015'],
                       [1630121132.999, '1627345015'], [1630121147.999, '1627345015'],
                       [1630121162.999, '1627345015'], [1630121177.999, '1627345015'],
                       [1630121192.999, '1627345015']]}}

    def test_init(self):
        data_manager = DataManager(self.data_list, self.host_list)
        new_data_list = [{
            "name": "node_cpu_frequency_hertz",
            "type": "kpi",
            "label": {
                "cpu": "1"
            },
            "macro": "$0",
            "data_name_str": 'node_cpu_frequency_hertz[["cpu", "1"]]',

        },
            {
                "name": "go_memstats_sys_bytes",
                "type": "log",
                "label": {
                    "cpu": "1",
                    "mode": "irq"

                },
                "macro": "$1",
                "data_name_str": 'go_memstats_sys_bytes[["cpu", "1"], ["mode", "irq"]]'
            },
            {
                "name": "node_boot_time_seconds",
                "type": "kpi",
                "macro": "$2",
                "data_name_str": 'node_boot_time_seconds[]'
            }]

        self.assertListEqual(data_manager.data_list, new_data_list)
        host_cache = {"90.90.64.64": {}, "90.90.64.65": {}, "90.90.64.66": {}}
        self.assertDictEqual(data_manager.host_cache, host_cache)
        data_map = {
            'node_cpu_frequency_hertz[["cpu", "1"]]': "$0",
            'go_memstats_sys_bytes[["cpu", "1"], ["mode", "irq"]]': "$1",
            'node_boot_time_seconds[]': "$2"
        }
        self.assertDictEqual(data_manager.data_name_map, data_map)
        self.assertEqual(data_manager.data_type, "log")

    def test_find_start_index(self):
        data_manager = DataManager(self.data_list, self.host_list)
        data_manager.host_cache = self.host_cache
        self.assertEqual(data_manager.find_start_index(None, None, 1630120922), -1)
        self.assertEqual(data_manager.find_start_index("90.90.64.84", "$0", 1630120922), -1)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$5", 1630120922), -1)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630120922), 0)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630120927.931), 0)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630120987), 4)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630120987.931), 4)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630121197.931), 18)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630121197), 18)
        self.assertEqual(data_manager.find_start_index("90.90.64.65", "$0", 1630121297), -1)

    @mock.patch("adoctor_check_executor.check_executor.data_manager.CheckMsgToolKit")
    def test_query_data(self, mock_check_msg_tool_kit):
        data_list = [{
            "name": "node_boot_time_seconds",
            "type": "kpi",
        }]
        data_manager = DataManager(data_list, self.host_list)
        response1 = {'code': 200, 'fail_list': [], 'msg': 'openration succeed', 'succeed_list': [
            {'host_id': '90.90.64.65', 'label': {}, 'name': 'node_boot_time_seconds',
             'values': [[1630120927.931, '1627981323'], [1630120942.931, '1627981323'],
                        [1630120957.931, '1627981323'], [1630120972.931, '1627981323'],
                        [1630120987.931, '1627981323'], [1630121002.931, '1627981323'],
                        [1630121017.931, '1627981323'], [1630121032.931, '1627981323'],
                        [1630121047.931, '1627981323'], [1630121062.931, '1627981323'],
                        [1630121077.931, '1627981323'], [1630121092.931, '1627981323'],
                        [1630121107.931, '1627981323'], [1630121122.931, '1627981323'],
                        [1630121137.931, '1627981323'], [1630121152.931, '1627981323'],
                        [1630121167.931, '1627981323'], [1630121182.931, '1627981323'],
                        [1630121197.931, '1627981323']]}]}
        response2 = {'code': 200, 'fail_list': ["node_boot_time_seconds"],
                     'msg': 'openration succeed',
                     'succeed_list': []}
        response3 = {'code': 200, 'fail_list': [],
                     'msg': 'openration succeed', 'succeed_list': []}
        check_item_config = {
            "check_item": "check_item1",
            "data_list": data_list,
            "condition": "$0>1",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        }
        host_cache = {'90.90.64.65': {
            '$0': [[1630120927.931, '1627981323'], [1630120942.931, '1627981323'],
                   [1630120957.931, '1627981323'], [1630120972.931, '1627981323'],
                   [1630120987.931, '1627981323'], [1630121002.931, '1627981323'],
                   [1630121017.931, '1627981323'], [1630121032.931, '1627981323'],
                   [1630121047.931, '1627981323'], [1630121062.931, '1627981323'],
                   [1630121077.931, '1627981323'], [1630121092.931, '1627981323'],
                   [1630121107.931, '1627981323'], [1630121122.931, '1627981323'],
                   [1630121137.931, '1627981323'], [1630121152.931, '1627981323'],
                   [1630121167.931, '1627981323'], [1630121182.931, '1627981323'],
                   [1630121197.931, '1627981323']]},
            '90.90.64.64': {},
            '90.90.64.66': {}}
        check_item_detail = CheckItemDetail("admin", check_item_config)
        mock_check_msg_tool_kit.get_data_from_database.side_effect = [response1,
                                                                      response2,
                                                                      response3]
        abnormal_data_list = []
        data_manager.query_data(self.host_list, check_item_detail,
                                [1630120927, 1630121198], abnormal_data_list)
        self.assertDictEqual(data_manager.host_cache, host_cache)
