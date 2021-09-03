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
Date: 2021/9/1 17:37
docs: test_check_item_manager.py
description: test check item manager
"""
import unittest
from unittest import mock
from adoctor_check_executor.check_executor.check_item_manager import check_item_manager


class TestCheckItemManager(unittest.TestCase):
    def setUp(self) -> None:
        self.check_item_config = {
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            }],
            "condition": "data_item1>1",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        }
        self.check_items = [{
            "check_item": "check_item1",
            "data_list": [{
                "name": "data_item1",
                "label": {
                    "mode": "irq"
                }
            }],
            "condition": "data_item1>1",
            "plugin": "",
            "label_config": "cpu",
            "description": "aaa"
        },
            {
                "check_item": "check_item2",
                "data_list": [{
                    "name": "data_item2",
                    "label": {
                        "mode": "irq"
                    }
                },
                    {
                        "name": "data_item3",
                        "label": {
                            "mode": "irq",
                            "device": "125s0f0"
                        }
                    }],
                "condition": "data_item2 + data_item3 < 10",
                "plugin": "",
                "label_config": "mode",
                "description": "bbb"
            }]

    def test_get_item(self):
        check_item_manager._add_check_item("admin1", self.check_item_config)
        check_item_manager._add_check_item("admin2", self.check_item_config)
        self.assertEqual(len(check_item_manager._cache["admin1"]), 1)
        self.assertEqual(len(check_item_manager._cache["admin2"]), 1)
        check_item_manager.clear("admin1")
        check_item_manager.clear("admin2")

    def test_clear(self):
        check_item_manager._add_check_item("admin", self.check_item_config)
        self.assertEqual(len(check_item_manager._cache["admin"]), 1, msg="Add check item")
        check_item_manager.clear("xxx")
        self.assertEqual(len(check_item_manager._cache["admin"]), 1, msg="Clear invalid user")
        check_item_manager.clear("admin")
        self.assertEqual(len(check_item_manager._cache["admin"]), 0, msg="Clear cache")
        check_item_manager.clear("admin")
        self.assertEqual(len(check_item_manager._cache["admin"]), 0, msg="Clear cache repeat")
        check_item_manager.clear("admin")

    def test_get_check_item_list(self):
        check_item_manager._add_check_item("admin1", self.check_item_config)
        self.assertEqual(len(check_item_manager._cache["admin1"]), 1)
        self.assertIsNone(check_item_manager.get_check_item_list("admin3"),
                          msg="Get check item list from invalid user")
        check_item_list1 = check_item_manager.get_check_item_list("admin1")
        self.assertEqual(len(check_item_list1), 1)
        check_item_manager.clear("admin1")

    def import_check_item(self):
        check_item_manager.import_check_item("admin1", self.check_items)
        self.assertEqual(len(check_item_manager._cache["admin1"]), 2)
        check_item_manager.clear("admin1")

    def test_delete_check_item(self):
        check_item_manager.import_check_item("admin1", self.check_items)
        check_item_list = ["check_item1", "check_item2", "check_item3"]
        check_item_manager.delete_check_item("admin1", check_item_list)
        self.assertEqual(len(check_item_manager._cache["admin1"]), 0)

    @mock.patch("adoctor_check_executor.check_executor.check_item_manager.CheckMsgToolKit")
    def test_query_check_rule(self, mock_check_toolkit):
        mock_check_toolkit.get_user_list_from_database.return_value = ["admin1", "admin2"]
        mock_check_toolkit.get_check_rule_from_database.side_effect = [self.check_items,
                                                                       self.check_items]
        check_item_manager.query_check_rule()
        self.assertListEqual(list(check_item_manager._cache.keys()), ["admin1", "admin2"])
        self.assertListEqual(list(check_item_manager._cache["admin1"].keys()),
                             ["check_item1", "check_item2"])
        self.assertListEqual(list(check_item_manager._cache["admin2"].keys()),
                             ["check_item1", "check_item2"])
        check_item_manager.clear("admin1")
        check_item_manager.clear("admin2")
