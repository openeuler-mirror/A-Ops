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
docs: test_expression_parser.py
description: test expression parser
"""
import unittest
from adoctor_check_executor.check_rule_plugins.expression_parser.parser import Parser
from adoctor_check_executor.check_rule_plugins.expression_parser.model import *
from ply.yacc import YaccProduction
from ply.lex import LexToken


def build_literal_yacc_production(literal_value, literal_type):
    yacc_prodution = YaccProduction([])
    sym1 = LexToken()
    sym1.type = 'Literal'
    sym1.value = None
    yacc_prodution.slice.append(sym1)
    sym2 = LexToken()
    sym2.type = literal_type
    sym2.value = literal_value
    yacc_prodution.slice.append(sym2)
    return yacc_prodution


one = Literal(build_literal_yacc_production('1', 'NUM'))
two = Literal(build_literal_yacc_production('2', 'NUM'))
three = Literal(build_literal_yacc_production('3', 'NUM'))
true = Literal(build_literal_yacc_production('True', 'TRUE'))
false = Literal(build_literal_yacc_production('False', 'FALSE'))
a = Name('a')
b = Name('b')
c = Name('c')
d = Name('d')
e = Name('e')

expression_bin_operator = [
    # simple test for each operator
    ('True', true, True),
    ('1+2', ArithmeticOperator('+', one, two), 3),
    ('a+b', ArithmeticOperator('+', a, b), None),
    (' 1 + 2 ', ArithmeticOperator('+', one, two), 3),
    ('1-2', ArithmeticOperator('-', one, two), -1),
    ('1*2', ArithmeticOperator('*', one, two), 2),
    ('1/2', ArithmeticOperator('/', one, two), 0.5),
    ('1%2', ArithmeticOperator('%', one, two), 1),
    ('1^2', BitOperation('^', one, two), 3),
    ('1&2', BitOperation('&', one, two), 0),
    ('1&&2', LogicalOperation('&&', one, two), 2),
    ('1|2', BitOperation('|', one, two), 3),
    ('1||2', LogicalOperation('||', one, two), 1),
    ('1==2', ComparisonOperator('==', one, two), False),
    ('1!=2', ComparisonOperator('!=', one, two), True),
    ('1<2', ComparisonOperator('<', one, two), True),
    ('1<=2', ComparisonOperator('<=', one, two), True),
    ('1>2', ComparisonOperator('>', one, two), False),
    ('1>=2', ComparisonOperator('>=', one, two), False),
    ('1<<2', BitOperation('<<', one, two), 4),
    ('1>>2', BitOperation('>>', one, two), 0),
    # left associativity
    ('1+2+3', ArithmeticOperator('+', ArithmeticOperator('+', one, two), three), 6),
    # precedence
    ('1+2*3', ArithmeticOperator('+', one, ArithmeticOperator('*', two, three)), 7),
    # parenthesized expressions
    ('(1+2)*3', ArithmeticOperator('*', ArithmeticOperator('+', one, two), three), 9),
    # conditionals
    ('a ? b : c', Conditional(a, b, c), None),
    ('a ? b ? c : d : e', Conditional(a, Conditional(b, c, d), e), None),
    ('a ? b : c ? d : e', Conditional(a, b, Conditional(c, d, e)), None),
    ('True ? 1 : 2', Conditional(true, one, two), 1),
    ('True ? False ? 1 : 2 : 3', Conditional(true, Conditional(false, one, two), three), 2),
    ('False ? 1 : True ? 2 : 3', Conditional(false, one, Conditional(true, two, three)), 2),
]

expression_unary_operator = [
    # unary expressions
    ('+a', Unary('+', a), None),
    ('+1', Unary('+', one), 1),
    ('-a', Unary('-', a), None),
    ('-1', Unary('-', one), -1),
    ('!a', Unary('!', a), None),
    ('!1', Unary('!', one), 0),
    ('!!a', Unary('!', Unary('!', a)), None),
    ('!!1', Unary('!', Unary('!', one)), 1),
    ('~a', Unary('~', a), None),
    ('~1', Unary('~', one), -2),
]

expression_function = [
    # method call
    ('bar()', FunctionCall(name='bar')),
    ('getName(1,2,3)', FunctionCall(name='getName', arguments=[one, two, three])),
    ('bar(1, b, c)', FunctionCall(name='bar', arguments=[one, b, c])),
    ('data.count(1,b,c)', FunctionCall(name='count',
                                       target=Name(value='data'),
                                       arguments=[one, b, c]))
]

expression_member = [
    # method call
    ('{1:2} in {1:2,3:1}',
     MemberOperation("in", Dict(pair_list=[Pair(one, two)]),
                     Dict(pair_list=[Pair(one, two), Pair(three, one)]))),
    ('{1:2} in {2:2,3:1}',
     MemberOperation("in", Dict(pair_list=[Pair(one, two)]),
                     Dict(pair_list=[Pair(two, two), Pair(three, one)]))),
    ('{1:2} notin {1:2,3:1}',
     MemberOperation("notin", Dict(pair_list=[Pair(one, two)]),
                     Dict(pair_list=[Pair(one, two), Pair(three, one)]))),
    ('{1:2} notin {2:2,3:1}',
     MemberOperation("notin", Dict(pair_list=[Pair(one, two)]),
                     Dict(pair_list=[Pair(two, two), Pair(three, one)]))),
    ('{a:a} in {a:b,c:1}',
     MemberOperation("in", Dict(pair_list=[Pair(a, a)]),
                     Dict(pair_list=[Pair(a, b), Pair(c, one)]))),
    ('{a:2} in {2:2,3:2}',
     MemberOperation("in", Dict(pair_list=[Pair(a, two)]),
                     Dict(pair_list=[Pair(two, two), Pair(three, two)]))),
    ('{a:b} notin {a:b,3:2}',
     MemberOperation("notin", Dict(pair_list=[Pair(a, b)]),
                     Dict(pair_list=[Pair(a, b), Pair(three, two)]))),
    ('{a:2} notin {2:2,3:2}',
     MemberOperation("notin", Dict(pair_list=[Pair(a, two)]),
                     Dict(pair_list=[Pair(two, two), Pair(three, two)])))

]


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def parse_and_cal_expression(self, expression):
        for expr, parse_result, calc_result in expression:
            print(expr)
            ret = self.parser.parse_string(expr)
            self.assertEqual(
                ret, parse_result, 'for {} got: {}, expected: {}'.format(expr, ret, parse_result))

    def test_expression_bin_operator(self):
        self.parse_and_cal_expression(expression_bin_operator)

    def test_parse_expression_unary_operator(self):
        self.parse_and_cal_expression(expression_unary_operator)

    def test_parse_expression_function(self):

        for expr, parse_result in expression_function:
            ret = self.parser.parse_string(expr)
            self.assertEqual(
                ret, parse_result, 'for {} got: {}, expected: {}'.format(expr, ret, parse_result))

    def test_parse_expression_member(self):
        i = 1
        for expr, parse_result in expression_member:
            print(i)
            i += 1
            ret = self.parser.parse_string(expr)

            self.assertEqual(
                type(ret), type(parse_result),
                'for {} got: {}, expected: {}'.format(expr, ret, parse_result))


class TestFunctioncall(unittest.TestCase):
    def test_get_function(self):
        self.assertSetEqual(set(FunctionCall.function_list.keys()),
                            {'builtin_keyword', 'builtin_diff', 'builtin_count', 'builtin_max',
                             'builtin_avg', 'builtin_sum', 'builtin_abschange',
                             'builtin_change', 'builtin_min'})


if __name__ == '__main__':
    unittest.main()
