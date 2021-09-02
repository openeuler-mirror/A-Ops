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
Date: 2021/8/24 0:04
docs: test_check_rule_manager.py
description: test check rule manager
"""
import os
import unittest
import shutil

from adoctor_check_executor.check_executor.check_rule_manager import check_rule_manager

HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCheckRuleManager(unittest.TestCase):
    def setUp(self) -> None:
        src_file = os.path.join("data", "test_rule_plugin.py")
        dst_file = os.path.join(HOME_PATH,
                                "adoctor_check_executor",
                                "check_rule_plugins",
                                "test_rule_plugin.py")

        shutil.copy(src_file, dst_file)

    def tearDown(self) -> None:
        dst_file = os.path.join(HOME_PATH,
                                "adoctor_check_executor",
                                "check_rule_plugins",
                                "test_rule_plugin.py")
        os.remove(dst_file)

    def test_load_plugins(self):
        self.assertIn("expression_rule_plugin", check_rule_manager.plugins.keys(),
                      msg="Load expression plugin rule success")

    def test_run_plugin(self):
        check_rule_manager.run_plugin("test_rule_plugin", "TestCheckRule", "test_rule_plugin")
        self.assertIn("test_rule_plugin", check_rule_manager.plugins.keys(),
                      msg="Load expression plugin rule success")

    def test_unload_plugin(self):
        check_rule_manager.run_plugin("test_rule_plugin", "TestCheckRule", "test_rule_plugin")
        check_rule_manager.unload_plugin("xxx")
        self.assertIn("test_rule_plugin", check_rule_manager.plugins.keys(),
                      msg="Load expression plugin rule success")
        check_rule_manager.unload_plugin("test_rule_plugin")
        self.assertNotIn("test_rule_plugin", check_rule_manager.plugins.keys(),
                         msg="Load expression plugin rule success")

    def test_get_plugin(self):
        check_rule_manager.run_plugin("test_rule_plugin", "TestCheckRule", "test_rule_plugin")
        self.assertIsNone(check_rule_manager.get_plugin("xxxx"),
                          msg="Load expression plugin rule success")
        test_plugin = check_rule_manager.get_plugin("test_rule_plugin")
        self.assertEqual(test_plugin.name, "test_check_rule",
                         msg="Load expression plugin rule success")


if __name__ == "__main__":
    unittest.main()
