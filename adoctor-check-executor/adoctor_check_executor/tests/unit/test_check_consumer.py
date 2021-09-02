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
Date: 2021/9/1 22:27
docs: test_check_consumer.py
description: test check consumer
"""

import unittest
from unittest import mock
from adoctor_check_executor.common.check_consumer import CheckConsumer, DoCheckConsumer, \
    DelRuleConsumer, ImportRuleConsumer
from adoctor_check_executor.common.constant import CheckTopic, CheckGroup
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.check_executor.check_item_manager import check_item_manager


class TestCheckConsumer(unittest.TestCase):
    def test_stop_consumer(self):
        consumer = CheckConsumer("test_topic", "test_group", executor_check_config)
        consumer.stop_consumer()
        self.assertFalse(consumer._running_flag)


class TestImportRuleConsumer(unittest.TestCase):
    def test_process_msgs(self):
        msg = {'check_items': [{'check_item': 'check_item1',
                                'data_list': [{'name': 'node_cpu_seconds_total',
                                               'type': 'kpi',
                                               'label': {'cpu': '1', 'mode': 'irq'}}],
                                'condition': '$0>1',
                                'plugin': '',
                                'description': 'aaa'},
                               {'check_item': 'check_item2',
                                'data_list': [{
                                    'name': 'node_cpu_frequency_min_hertz',
                                    'type': 'kpi',
                                    'label': {'cpu': '1'}},
                                    {'name': 'node_cpu_guest_seconds_total',
                                     'type': 'kpi',
                                     'label': {'cpu': '1', 'mode': 'nice'}}],
                                'condition': '$0 + $1 < 10',
                                'plugin': '',
                                'description': 'bbb'}, ],
               'username': 'admin'}
        import_rule_consumer = ImportRuleConsumer(CheckTopic.retry_check_topic,
                                                  CheckGroup.retry_check_group_id,
                                                  executor_check_config)
        import_rule_consumer._process_msgs(msg)
        self.assertEqual(len(check_item_manager._cache.get("admin")), 2)
        check_item_manager.clear("admin")


class TestDeleteRuleConsumer(unittest.TestCase):
    def test_process_msgs(self):
        check_items = [{'check_item': 'check_item1',
                        'data_list': [{'name': 'node_cpu_seconds_total',
                                       'type': 'kpi',
                                       'label': {'cpu': '1', 'mode': 'irq'}}],
                        'condition': '$0>1',
                        'plugin': '',
                        'description': 'aaa'},
                       {'check_item': 'check_item2',
                        'data_list': [{
                            'name': 'node_cpu_frequency_min_hertz',
                            'type': 'kpi',
                            'label': {'cpu': '1'}},
                            {'name': 'node_cpu_guest_seconds_total',
                             'type': 'kpi',
                             'label': {'cpu': '1', 'mode': 'nice'}}],
                        'condition': '$0 + $1 < 10',
                        'plugin': '',
                        'description': 'bbb'}, ]
        check_item_manager.import_check_item("user", check_items)
        import_rule_consumer = DelRuleConsumer(CheckTopic.delete_check_rule_topic,
                                               CheckGroup.delete_check_rule_group_id,
                                               executor_check_config)
        msg = {
            "check_items": ["check_item1", "check_item7"]
        }
        import_rule_consumer._process_msgs(msg)
        self.assertEqual(len(check_item_manager._cache.get("admin")), 2)
        check_item_manager.clear("admin")


class TestDoCheckConsumer(unittest.TestCase):
    @mock.patch("adoctor_check_executor.common.check_consumer.CheckTask")
    def test_process_msgs(self, mock_check_task):
        msg = {'task_id': -1, 'user': 'admin',
               'host_list': [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                              'public_ip': '90.90.64.65'},
                             {'host_id': 'f485bd26070211ecaa06a01c8d75c8f3',
                              'public_ip': '90.90.64.64'},
                             {'host_id': 'fa05c1ba070211ecad52a01c8d75c8f3',
                              'public_ip': '90.90.64.66'}],
               'check_items': [], 'time_range': [1630565312, 1630565342]}
        mock_check_task.do_check.import_check_items = None
        mock_check_task.do_check.return_value = None
        import_rule_consumer = DoCheckConsumer(CheckTopic.do_check_topic,
                                               CheckGroup.do_check_group_id,
                                               executor_check_config)
        import_rule_consumer._process_msgs(msg)
        self.assertEqual(len(check_item_manager._cache.get("admin")), 2)
