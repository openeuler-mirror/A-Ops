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
Date: 2021/9/1 19:16
docs: test_expression_rule.py
description: test expression rule
"""

import unittest
from adoctor_check_executor.check_rule_plugins.expression_rule import ExpressionCheckRule
from adoctor_check_executor.common.check_error import CheckItemError, CheckPluginError


class TestExpressionRulePlugin(unittest.TestCase):
    def test_analysis_expression(self):
        expression_check_rule = ExpressionCheckRule()
        expression_check_rule.analysis_expression("1+1>2")
        self.assertEqual(expression_check_rule.time_shift, 0)
        expression_check_rule.analysis_expression("max(1s)")
        self.assertEqual(expression_check_rule.time_shift, 1)
        expression_check_rule.analysis_expression("max(#1)")
        self.assertEqual(expression_check_rule.time_shift, 15)
        expression_check_rule.analysis_expression("max(1m)")
        self.assertEqual(expression_check_rule.time_shift, 60)
        expression_check_rule.analysis_expression("max(1h)")
        self.assertEqual(expression_check_rule.time_shift, 3600)

    def test_get_time_shift(self):
        expression_check_rule = ExpressionCheckRule()
        expression_check_rule._visitor.num_shift = 5
        expression_check_rule._visitor.time_shift = 60
        expression_check_rule._get_time_shift()
        self.assertEqual(expression_check_rule.time_shift, 75)

    def test_judge_condition(self):
        data_vector = {
            '$0': [[1630120927.931, '1627981323'], [1630120942.931, '1627981323'],
                   [1630120957.931, '1627981323'],
                   [1630120972.931, '1627981323'], [1630120987.931, '1627981323'],
                   [1630121002.931, '1627981323'],
                   [1630121017.931, '1627981323'], [1630121032.931, '1627981323'],
                   [1630121047.931, '1627981323']],
            '$1': [[1630120931.143, '1627527809'], [1630120946.143, '1627527809'],
                   [1630120961.143, '1627527809'],
                   [1630120976.143, '1627527809'], [1630120991.143, '1627527809'],
                   [1630121006.143, '1627527809'],
                   [1630121021.143, '1627527809'], [1630121036.143, '1627527809'],
                   [1630121051.143, '1627527809']]
        }
        expression_check_rule = ExpressionCheckRule()
        with self.assertRaises(CheckItemError, msg="Expression not parsed"):
            expression_check_rule.judge_condition(1, data_vector, "$0")
        expression_check_rule.analysis_expression("$0+$1>10000.235")
        self.assertTrue(expression_check_rule.judge_condition(1, data_vector, "$0"))
        self.assertTrue(expression_check_rule.judge_condition(0, data_vector, "$0"))
        with self.assertRaises(CheckPluginError, msg="Invalid index"):
            self.assertTrue(expression_check_rule.judge_condition(10, data_vector, "$0"))
            self.assertTrue(expression_check_rule.judge_condition(5, data_vector, "$7"))
