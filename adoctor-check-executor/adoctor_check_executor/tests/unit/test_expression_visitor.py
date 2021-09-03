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
Date: 2021/8/6 21:49
docs: test_expression_visitor.py
description: test expression visitor
"""
import unittest
from adoctor_check_executor.check_rule_plugins.expression_parser.visitor import ShiftVisitor
from adoctor_check_executor.check_rule_plugins.expression_parser.parser import Parser

test_expression = [
    ('data_10m.diff(#1) && data_b22.max(2s)>10', 1, 2),
    ('data_10m.diff(#10) && data_b22.max(2h)>10', 10, 7200)
]


class TestVisitor(unittest.TestCase):
    def test_visitor(self):
        parser = Parser()
        for expression, num_shift, time_shift in test_expression:
            tree = parser.parse_string(expression)
            visitor = ShiftVisitor()
            tree.traverse(visitor)
            self.assertEqual(visitor.time_shift, time_shift)
            self.assertEqual(visitor.num_shift, num_shift)


if __name__ == '__main__':
    unittest.main()
