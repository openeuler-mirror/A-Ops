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
Date: 2021/8/5 15:17
docs: parser.py
description: expression parser
"""

import ply.lex as lex
import ply.yacc as yacc
from adoctor_check_executor.check_rule_plugins.expression_parser.model import Conditional, \
    ArithmeticOperator, ComparisonOperator, LogicalOperation, BitOperation, Unary, \
    TimeFilter, NumFilter, FunctionCall, Literal, Pair, Dict, Name, MemberOperation
from adoctor_check_executor.common.check_error import ExpressionError
from aops_utils.log.log import LOGGER


class Lexer:
    """
    Lexer definition
    """
    keywords = (
        'null', 'in', 'notin',
        'true', 'false', 'True', 'False', 'TRUE', 'FALSE',
    )

    tokens = [
                 'NAME', 'MARCO',
                 'NUM', 'MIN', 'SEC', 'HOUR', 'SCI_NUM',
                 'CHAR_LITERAL',
                 'STRING_LITERAL',
                 'OR', 'AND',
                 'EQ', 'NEQ', 'GTEQ', 'LTEQ',
                 'LSHIFT', 'RSHIFT', 'RRSHIFT',
                 'NUM_FILTER'
             ] + [k.upper() for k in keywords]
    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_NUM = r'\.?[0-9][0-9eE_lLdDa-fA-F.xXpP]*'
    t_SCI_NUM = r'-?([1-9]{1}|[1-9]?\.[0-9]+)[eE][+\-]?0?[1-9]+0*'
    t_CHAR_LITERAL = r'\'([^\\\n]|(\\.))*?\''
    t_STRING_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

    t_OR = r'\|\|'
    t_AND = '&&'
    t_MIN = 'm'
    t_SEC = 's'
    t_HOUR = 'h'
    t_NUM_FILTER = r'\#[1-9]\d*'

    t_EQ = '=='
    t_NEQ = '!='
    t_GTEQ = '>='
    t_LTEQ = '<='

    t_LSHIFT = '<<'
    t_RSHIFT = '>>'
    t_RRSHIFT = '>>>'

    t_ignore = ' \t\f'

    t_MACRO = r'\$[0-9]*'

    @staticmethod
    def t_NAME(token):
        '[A-Za-z_$][A-Za-z0-9_$]*'
        if token.value in Lexer.keywords:
            token.type = token.value.upper()
            return token
        if token.value == 'm':
            token.type = 'MIN'
        elif token.value == 's':
            token.type = 'SEC'

        elif token.value == 'h':
            token.type = 'HOUR'

        return token

    @staticmethod
    def t_newline(token):
        r'\n+'
        token.lexer.lineno += len(token.value)

    @staticmethod
    def t_newline2(token):
        r'(\r\n)+'
        token.lexer.lineno += len(token.value) / 2

    @staticmethod
    def t_error(token):
        """
        error lex token
        """
        LOGGER.error("Illegal character '%s' (%s) in line %s", token.value[0],
                                                              hex(ord(token.value[0])),
                                                              token.lexer.lineno)
        raise ExpressionError('error: {}'.format(token))


class ExpressionParser:
    """
    Expression parser
    """

    @staticmethod
    def p_expression(production):
        '''expression : conditional_expression'''
        production[0] = production[1]

    @staticmethod
    def p_expression_not_name(production):
        '''expression_not_name : conditional_expression_not_name'''
        production[0] = production[1]

    @staticmethod
    def p_conditional_expression(production):
        '''conditional_expression : conditional_or_expression
                                  | conditional_or_expression '?' expression ':' conditional_expression'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Conditional(production[1], production[3], production[5])

    @staticmethod
    def p_conditional_expression_not_name(production):
        '''conditional_expression_not_name : conditional_or_expression_not_name
                                           | conditional_or_expression_not_name '?' expression ':' conditional_expression
                                           | name '?' expression ':' conditional_expression'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Conditional(production[1], production[3], production[5])

    @staticmethod
    def binop(production, ctor):
        """
        Constructing Binary Operations
        Args:
            production (YaccProduction): yacc production
            ctor (BinaryExpression) :Class to be instantiated
        """
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = ctor(production[2], production[1], production[3])
    @staticmethod
    def p_conditional_or_expression(production):
        '''conditional_or_expression : conditional_and_expression
                                     | conditional_or_expression OR conditional_and_expression'''
        ExpressionParser.binop(production, LogicalOperation)

    @staticmethod
    def p_conditional_or_expression_not_name(production):
        '''conditional_or_expression_not_name : conditional_and_expression_not_name
                                              | conditional_or_expression_not_name OR conditional_and_expression
                                              | name OR conditional_and_expression'''
        ExpressionParser.binop(production, LogicalOperation)

    @staticmethod
    def p_conditional_and_expression(production):
        '''conditional_and_expression : inclusive_or_expression
                                      | conditional_and_expression AND inclusive_or_expression'''
        ExpressionParser.binop(production, LogicalOperation)

    @staticmethod
    def p_conditional_and_expression_not_name(production):
        '''conditional_and_expression_not_name : inclusive_or_expression_not_name
                                               | conditional_and_expression_not_name AND inclusive_or_expression
                                               | name AND inclusive_or_expression'''
        ExpressionParser.binop(production, LogicalOperation)

    @staticmethod
    def p_inclusive_or_expression(production):
        '''inclusive_or_expression : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_inclusive_or_expression_not_name(production):
        '''inclusive_or_expression_not_name : exclusive_or_expression_not_name
                                            | inclusive_or_expression_not_name '|' exclusive_or_expression
                                            | name '|' exclusive_or_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_exclusive_or_expression(production):
        '''exclusive_or_expression : and_expression
                                   | exclusive_or_expression '^' and_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_exclusive_or_expression_not_name(production):
        '''exclusive_or_expression_not_name : and_expression_not_name
                                            | exclusive_or_expression_not_name '^' and_expression
                                            | name '^' and_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_and_expression(production):
        '''and_expression : equality_expression
                          | and_expression '&' equality_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_and_expression_not_name(production):
        '''and_expression_not_name : equality_expression_not_name
                                   | and_expression_not_name '&' equality_expression
                                   | name '&' equality_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_equality_expression(production):
        '''equality_expression : relational_expression
                               | equality_expression EQ relational_expression
                               | equality_expression NEQ relational_expression '''
        ExpressionParser.binop(production, ComparisonOperator)

    @staticmethod
    def p_equality_expression_not_name(production):
        '''equality_expression_not_name : relational_expression_not_name
                                        | equality_expression_not_name EQ relational_expression
                                        | name EQ relational_expression
                                        | equality_expression_not_name NEQ relational_expression
                                        | name NEQ relational_expression '''
        ExpressionParser.binop(production, ComparisonOperator)

    @staticmethod
    def p_membership_expression(production):
        '''equality_expression : dict IN dict
                               | dict NOTIN dict '''
        ExpressionParser.binop(production, MemberOperation)

    @staticmethod
    def p_relational_expression(production):
        '''relational_expression : shift_expression
                                 | relational_expression '>' shift_expression
                                 | relational_expression '<' shift_expression
                                 | relational_expression GTEQ shift_expression
                                 | relational_expression LTEQ shift_expression '''
        ExpressionParser.binop(production, ComparisonOperator)

    @staticmethod
    def p_relational_expression_not_name(production):
        '''relational_expression_not_name : shift_expression_not_name
                                          | shift_expression_not_name '<' shift_expression
                                          | name '<' shift_expression
                                          | shift_expression_not_name '>' shift_expression
                                          | name '>' shift_expression
                                          | shift_expression_not_name GTEQ shift_expression
                                          | name GTEQ shift_expression
                                          | shift_expression_not_name LTEQ shift_expression
                                          | name LTEQ shift_expression'''
        ExpressionParser.binop(production, ComparisonOperator)

    @staticmethod
    def p_shift_expression(production):
        '''shift_expression : additive_expression
                            | shift_expression LSHIFT additive_expression
                            | shift_expression RSHIFT additive_expression
                            | shift_expression RRSHIFT additive_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_shift_expression_not_name(production):
        '''shift_expression_not_name : additive_expression_not_name
                                     | shift_expression_not_name LSHIFT additive_expression
                                     | name LSHIFT additive_expression
                                     | shift_expression_not_name RSHIFT additive_expression
                                     | name RSHIFT additive_expression
                                     | shift_expression_not_name RRSHIFT additive_expression
                                     | name RRSHIFT additive_expression'''
        ExpressionParser.binop(production, BitOperation)

    @staticmethod
    def p_additive_expression(production):
        '''additive_expression : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression'''
        ExpressionParser.binop(production, ArithmeticOperator)

    @staticmethod
    def p_additive_expression_not_name(production):
        '''additive_expression_not_name : multiplicative_expression_not_name
                                        | additive_expression_not_name '+' multiplicative_expression
                                        | name '+' multiplicative_expression
                                        | additive_expression_not_name '-' multiplicative_expression
                                        | name '-' multiplicative_expression'''
        ExpressionParser.binop(production, ArithmeticOperator)

    @staticmethod
    def p_multiplicative_expression(production):
        '''multiplicative_expression : unary_expression
                                     | multiplicative_expression '*' unary_expression
                                     | multiplicative_expression '/' unary_expression
                                     | multiplicative_expression '%' unary_expression'''
        ExpressionParser.binop(production, ArithmeticOperator)

    @staticmethod
    def p_multiplicative_expression_not_name(production):
        '''multiplicative_expression_not_name : unary_expression_not_name
                                              | multiplicative_expression_not_name '*' unary_expression
                                              | name '*' unary_expression
                                              | multiplicative_expression_not_name '/' unary_expression
                                              | name '/' unary_expression
                                              | multiplicative_expression_not_name '%' unary_expression
                                              | name '%' unary_expression'''
        ExpressionParser.binop(production, ArithmeticOperator)

    @staticmethod
    def p_unary_expression(production):
        '''unary_expression : '+' unary_expression
                            | '-' unary_expression
                            | unary_expression_not_plus_minus'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Unary(production[1], production[2])

    @staticmethod
    def p_unary_expression_not_name(production):
        '''unary_expression_not_name : '+' unary_expression
                                     | '-' unary_expression
                                     | unary_expression_not_plus_minus_not_name'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Unary(production[1], production[2])

    @staticmethod
    def p_unary_expression_not_plus_minus(production):
        '''unary_expression_not_plus_minus : postfix_expression
                                           | '~' unary_expression
                                           | '!' unary_expression'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Unary(production[1], production[2])

    @staticmethod
    def p_unary_expression_not_plus_minus_not_name(production):
        '''unary_expression_not_plus_minus_not_name : postfix_expression_not_name
                                                    | '~' unary_expression
                                                    | '!' unary_expression'''
        if len(production) == 2:
            production[0] = production[1]
        else:
            production[0] = Unary(production[1], production[2])

    @staticmethod
    def p_postfix_expression(production):
        '''postfix_expression : primary
                              | name '''
        production[0] = production[1]

    @staticmethod
    def p_postfix_expression_not_name(production):
        '''postfix_expression_not_name : primary '''
        production[0] = production[1]

    @staticmethod
    def p_primary(production):
        '''primary : primary_no_new_array'''
        production[0] = production[1]

    @staticmethod
    def p_primary_no_new_array(production):
        '''primary_no_new_array : literal
                                | function_call'''
        production[0] = production[1]

    @staticmethod
    def p_primary_no_new_array2(production):
        '''primary_no_new_array : '(' name ')'
                                | '(' expression_not_name ')' '''
        production[0] = production[2]


class FunctionParser:
    """
    Function parser
    """

    @staticmethod
    def p_function_call(production):
        '''function_call : NAME '(' argument_list_opt ')' '''
        production[0] = FunctionCall(production[1], arguments=production[3])

    @staticmethod
    def p_function_call_data_name(production):
        '''function_call : name '.' NAME '(' argument_list_opt ')' '''
        production[0] = FunctionCall(production[3], target=production[1], arguments=production[5])

    @staticmethod
    def p_argument_list_opt(production):
        '''argument_list_opt : argument_list'''
        production[0] = production[1]

    @staticmethod
    def p_argument_list_opt_empty(production):
        '''argument_list_opt : empty'''
        production[0] = []

    @staticmethod
    def p_argument_list(production):
        '''argument_list : expression
                         | argument_list ',' expression'''
        if len(production) == 2:
            production[0] = [production[1]]
        else:
            production[0] = production[1] + [production[3]]

    @staticmethod
    def p_argument_list_time_filter(production):
        '''argument_list : time_filter
                         | time_filter ',' argument_list '''
        if len(production) == 2:
            production[0] = [production[1]]
        else:
            production[0] = [production[1]] + production[3]

    @staticmethod
    def p_argument_list_num_filter(production):
        '''argument_list : num_filter
                         | num_filter ',' argument_list '''
        if len(production) == 2:
            production[0] = [production[1]]
        else:
            production[0] = [production[1]] + production[3]

    @staticmethod
    def p_time_filter(production):
        ''' time_filter : NUM MIN
                        | NUM SEC
                        | NUM HOUR '''
        production[0] = TimeFilter(production[1], production[2])

    @staticmethod
    def p_num_filter(production):
        ''' num_filter : NUM_FILTER '''
        production[0] = NumFilter(production[1])


class TypeParser:
    """
    Type parser
    """

    @staticmethod
    def p_name(production):
        '''name : simple_name'''
        production[0] = production[1]

    @staticmethod
    def p_simple_name(production):
        '''simple_name : NAME
                       | MARCO '''
        production[0] = Name(production[1])

    @staticmethod
    def p_literal(production):
        '''literal : NUM
                   | SCI_NUM
                   | CHAR_LITERAL
                   | STRING_LITERAL
                   | TRUE
                   | FALSE
                   | NULL'''
        production[0] = Literal(production)

    @staticmethod
    def p_pair_list(production):
        '''pair_list : pair
                     | pair_list ',' pair '''
        if len(production) == 2:
            production[0] = [production[1]]
        else:
            production[1].append(production[3])
            production[0] = production[1]

    @staticmethod
    def p_pair(production):
        '''pair : name ':' name
                | literal ':' literal
                | name ':' literal
                | literal ':' name '''
        production[0] = Pair(production[1], production[3])

    @staticmethod
    def p_dict(production):
        '''dict : '{' '}'
                | '{' pair_list '}' '''
        if len(production) == 2:
            production[0] = {}
        else:
            production[0] = Dict(production[2])


class YaccParser(ExpressionParser, TypeParser, FunctionParser):
    """
    Yacc Parser
    """
    tokens = Lexer.tokens

    @staticmethod
    def p_error(production):
        """
        error yacc production
        """
        raise ExpressionError('error: {}'.format(production))

    @staticmethod
    def p_empty(production):
        '''empty :'''


class Parser:
    """
    Parser of expression str

    Attributes:
        lexer (lex): lexer
        parser (yacc): yacc
    """

    def __init__(self):
        """
        Constructor
        """
        self.lexer = lex.lex(module=Lexer(), optimize=True)
        self.parser = yacc.yacc(module=YaccParser(), optimize=True)

    def tokenize_string(self, expression_str):
        """
        Tokenize expression string

        Args:
            expression_str (str): expression str
        """
        self.lexer.input(expression_str)
        for token in self.lexer:
            print(token)

    def parse_string(self, expression_str, debug=0):
        """
        Parse expression str
        Args:
            expression_str (str): expression str
            debug (int): debug switch

        Return:
            dict
        """
        return self.parser.parse(expression_str, lexer=self.lexer, debug=debug)
