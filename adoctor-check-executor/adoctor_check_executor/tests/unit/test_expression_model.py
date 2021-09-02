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
Date: 2021/8/6 15:25
docs: test_expression_model.py
description: test expression model
"""
import unittest
from adoctor_check_executor.check_rule_plugins.expression_parser.parser import Parser
from adoctor_check_executor.check_rule_plugins.expression_parser.data_backpack import DataBackpack

expression_bin_operator = [
    # simple test for each operator
    ('True', True),
    ('1+2', 3),
    (' 1 + 2 ', 3),
    ('1-2', -1),
    ('1*2', 2),
    ('1/2', 0.5),
    ('1%2', 1),
    ('1^2', 3),
    ('1&2', 0),
    ('1&&2', 2),
    ('1|2', 3),
    ('1||2', 1),
    ('1==2', False),
    ('1!=2', True),
    ('1<2', True),
    ('1<=2', True),
    ('1>2', False),
    ('1>=2', False),
    ('1<<2', 4),
    ('1>>2', 0),
    # left associativity
    ('1+2+3', 6),
    # precedence
    ('1+2*3', 7),
    # parenthesized expressions
    ('(1+2)*3', 9),
    # conditionals
    ('True ? 1 : 2', 1),
    ('True ? False ? 1 : 2 : 3', 2),
    ('False ? 1 : True ? 2 : 3', 2),
]

expression_unary_operator = [
    # unary expressions
    ('+1', 1),
    ('-1', -1),
    ('!1', 0),
    ('!!1', 1),
    ('~1', -2),
]

data_vector = {'data11_a': [(1000001, 1), (1000001, 2), (1000003, 3), (1000004, 4), (1000005, 5)],
               'data_b22': [(1000001, 2), (1000002, 2), (1000003, 2), (1000004, 2), (1000005, 2)],
               'data_10m': [(1000001, 5), (1000002, 4), (1000003, 3), (1000004, 2), (1000005, 1)],
               'data11_d': [(1000001, 40), (1000002, 96), (1000003, 82),
                            (1000004, 74), (1000005, 68)],
               'data11_e': [(1000001, 4.5), (1000002, 5.6), (1000003, 6.8),
                            (1000004, 7.1), (1000005, 8.0)],
               'data11_f': [(1000001, "error"), (1000002, "nomal"),
                            (1000003, "error"), (1000004, "nomal"),
                            (1000005, "error")]}

expression_bin_operator_substitute = [
    ('data11_a+data_b22', 6),
    ('data11_a-1', 3),
    ('data11_a*data_10m', 8),
    ('data11_a/4', 1),
    ('data11_a%2', 0),
    ('1^data_b22', 3),
    ('1&data_10m', 0),
    ('data_10m&&2', 2),
    ('data11_a|2', 6),
    ('data_b22||2', 2),
    ('data_b22>2 ||data_10m<=2', True),
    ('data11_a==2', False),
    ('data_b22!=2', False),
    ('data_10m<.0', False),
    ('1.5<=data11_a', True),
    ('1.6>data_b22', False),
    ('data11_a>=data_b22', True),
    ('data11_a>data_b22 ? data_b22 : data_10m', 2),
    ('data11_a==1 ? 5>data_10m ? data_10m : data11_d : data11_e', 7.1),
    ('data11_a!=3 ? data_b22 : 0.1>data_10m ? data11_d : data11_e', 2),
]

expression_unary_operator_substitute = [
    ('+data11_a', 4),
    ('-data11_a', -4),
    ('!data11_a', 0),
    ('!!data11_a', 1),
    ('~data11_a', -5),
]

expression_member = [
    # method call
    ('{1:2} in {1:2,3:1}', True),
    ('{1:2} in {2:2,3:1}', False),
    ('{1:2} notin {1:2,3:1}', False),
    ('{1:2} notin {2:2,3:1}', True),
]

expression_member_substitute = [
    # method call
    ('{data11_a:data_b22} in {data11_a:data_b22,3:1}', True),
    ('{1:data_10m} in {data_10m:2,3:1}', False),
    ('{data_b22:2} notin {data_b22:2,3:1}', False),
    ('{1:data11_f} notin {2:data11_f,3:1}', True),
]


class TestCommonCalculate(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_expression_bin_operator(self):
        for expr, calc_result in expression_bin_operator:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("", 0, {})
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_expression_unary_operator(self):
        for expr, calc_result in expression_unary_operator:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("", 0, {})
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_expression_member_operator(self):
        for expr, calc_result in expression_member:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("", 0, {})
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))


class TestSubstituteCalculate(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_expression_bin_operator(self):
        for expr, calc_result in expression_bin_operator_substitute:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("data11_f", 3, data_vector)
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_expression_unary_operator(self):
        for expr, calc_result in expression_unary_operator_substitute:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("data11_f", 3, data_vector)
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_expression_memeber_operator(self):
        for expr, calc_result in expression_member_substitute:
            print(expr)
            tree = self.parser.parse_string(expr)
            data_backpack = DataBackpack("data11_f", 3, data_vector)
            ret = tree.calculate(data_backpack)
            self.assertEqual(ret, calc_result,
                             'for {} got: {}, expected: {}'.format(expr, ret, calc_result))


class TestFunctionCall(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_count_function(self):
        expr = 'count(10m, 3, "<")>1'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("data11_a", 3, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

        expr = 'data11_f.count(5s, "error", "==")==2'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 3, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_keyword_function(self):
        expr = 'data11_f.keyword("no")'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = False
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

        data_backpack = DataBackpack("", 3, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_max_function(self):
        expr = 'data_b22.max(2s)>10'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = False
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_diff_function(self):
        expr = 'data_10m.diff(#1)'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_min_function(self):
        expr = 'data_b22.min(#1)<10'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_change_function(self):
        expr = 'data_b22.change(#1)<10'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_abschange_function(self):
        expr = 'data_b22.abschange(#1)<10'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_avg_function(self):
        expr = 'data_b22.avg(#3)<5'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))

    def test_sum_function(self):
        expr = 'data_b22.sum(#3)>5'
        tree = self.parser.parse_string(expr)
        data_backpack = DataBackpack("", 4, data_vector)
        ret = tree.calculate(data_backpack)
        calc_result = True
        self.assertEqual(ret, calc_result,
                         'for {} got: {}, expected: {}'.format(expr, ret, calc_result))


if __name__ == '__main__':
    unittest.main()
