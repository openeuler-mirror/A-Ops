#!/usr/bin/python3
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
Date: 2021/8/7 17:10
docs: model.py
description: Expression analyse model
"""
import ast
import os
import operator

import adoctor_check_executor.check_rule_plugins. \
    expression_parser.builtin_function as builtin_function
from adoctor_check_executor.common.check_error import ExpressionError

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class SourceElement:
    """
    A SourceElement is the base class for all elements parsed by ply.

    Attributes:
        _fields (list): member
    """

    def __init__(self):
        """
            Constructor
        """
        self._fields = []

    def __repr__(self):
        """
            repr
        """
        equals = ("{0}={1!r}".format(k, getattr(self, k))
                  for k in self._fields)
        args = ", ".join(equals)
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        """
            equal
        """
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        """
            not equal
        """
        return not self.__dict__ == other.__dict__

    def traverse(self, visitor):
        """
        Traverse child nodes according to the storage sequence of child nodes in the self_field.
        Args:
            visitor (Visitor): traversal visitor
        """
        class_name = self.__class__.__name__
        visit = getattr(visitor, 'visit_' + class_name, None)
        if visit:
            visit(self)
        for field_name in self._fields:
            field = getattr(self, field_name)
            if not field:
                return
            if isinstance(field, list):
                for elem in field:
                    if isinstance(elem, SourceElement):
                        elem.traverse(visitor)
            elif isinstance(field, SourceElement):
                field.traverse(visitor)
            else:
                continue

    @staticmethod
    def get_real_value(key_name, data_backpack):
        """
        Get real data value of data name
        Args:
            key_name (str): data name
            data_backpack (DataBackpack): data cache

        Raise:
            ExpressionError
        """
        if key_name not in data_backpack.data_vector.keys():
            raise ExpressionError("Can not find key_name %s" % key_name)
        if data_backpack.target_index > len(data_backpack.data_vector[key_name]):
            raise ExpressionError("Index %d is invalid" % data_backpack.target_index)

        return data_backpack.get_data_value(data_backpack.target_index, key_name)

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache
        """


class Expression(SourceElement):
    """
    Expression Node

    Attributes:
        _fields (list): member
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self._fields = []


class BinaryExpression(Expression):
    """
    Binary operation expression

    Attributes:
        _fields (list): member
        sign (str): operator sign
        left_element (Expression): left element
        right_element (Expression): right element
        type (type): object type
    """

    def __init__(self, sign, left_element, right_element):
        """
        Constructor

        Args:
            sign (str): operator sign
            left_element (Expression/Number): left element
            right_element (Expression/Number): right element
        """
        super().__init__()
        self._fields = ['sign', 'left_element', 'right_element', 'type']
        self.sign = sign
        self.left_element = left_element
        self.right_element = right_element
        self.type = type(self)

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data

        Return:
            value
        """


class Conditional(Expression):
    """
    Conditional operation expression

    Attributes:
        _fields (list): member
        predicate (Expression/Name): Prejudgment condition
        if_true (Expression/Name): if true element
        if_false (Expression/Name): if false element
    """

    def __init__(self, predicate, if_true, if_false):
        """
        Constructor

        Args:
            predicate (Expression/Name): Prejudgment condition
            if_true (Expression/Name): if true element
            if_false (Expression/Name): if false element
        """
        super().__init__()
        self._fields = ['predicate', 'if_true', 'if_false']
        self.predicate = predicate
        self.if_true = if_true
        self.if_false = if_false

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value (bool)

        Raise:
            ExpressionError
        """
        predicate = self.predicate.calculate(data_backpack)
        if_true = self.if_true.calculate(data_backpack)
        if_false = self.if_false.calculate(data_backpack)
        if predicate is None or if_true is None or if_false is None:
            raise ExpressionError("Predicate or if_true or if_false is none")
        if predicate:
            return if_true
        return if_false


class ArithmeticOperator(BinaryExpression):
    """
    Arithmetic operation expression
    """

    @staticmethod
    def _get_operator_function(op_sign):
        """
        Get operator function from sign
        Args:
            op_sign (str): operator sign

        Returns:
            operator function
        """
        return {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '%': operator.mod,
        }[op_sign]

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raise:
            ExpressionError
        """
        left = self.left_element.calculate(data_backpack)
        right = self.right_element.calculate(data_backpack)
        if left is None or right is None:
            raise ExpressionError("left or right is none")
        operator_func = self._get_operator_function(self.sign)

        if self.sign in ('/', '%') and right == 0:
            raise ExpressionError("Attempt to divide by 0")

        return operator_func(left, right)


class ComparisonOperator(BinaryExpression):
    """
    Comparison operation expression
    """

    @staticmethod
    def _get_operator_function(op_sign):
        """
        Get operator function from sign
        Args:
            op_sign (str): operator sign

        Returns:
            operator function
        """
        return {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
        }[op_sign]

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raise:
            ExpressionError
        """
        left = self.left_element.calculate(data_backpack)
        right = self.right_element.calculate(data_backpack)
        if left is None or right is None:
            raise ExpressionError("left or right is none")
        operator_func = self._get_operator_function(self.sign)

        return operator_func(left, right)


class LogicalOperation(BinaryExpression):
    """
    Logical operation expression
    """

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raise:
            ExpressionError
        """
        left = self.left_element.calculate(data_backpack)
        right = self.right_element.calculate(data_backpack)
        if left is None or right is None:
            raise ExpressionError("left or right is none")

        if self.sign == '||':
            return left or right
        if self.sign == '&&':
            return left and right
        raise ExpressionError("Invalid sign %s " % self.sign)


class BitOperation(BinaryExpression):
    """
    Bit operation expression
    """

    @staticmethod
    def _get_operator_function(op_sign):
        """
        Get operator function from sign
        Args:
            op_sign (str): operator sign

        Returns:
            operator function
        """
        return {
            '<<': operator.lshift,
            '>>': operator.rshift,
            '|': operator.or_,
            '&': operator.and_,
            '^': operator.xor,
        }[op_sign]

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raise:
            ExpressionError
        """
        left = self.left_element.calculate(data_backpack)
        right = self.right_element.calculate(data_backpack)
        if left is None or right is None:
            raise ExpressionError("left or right is none")

        operator_func = self._get_operator_function(self.sign)

        return operator_func(int(left), int(right))


class MemberOperation(BinaryExpression):
    """
    Member operation expression
    """

    @staticmethod
    def _judge_member(left_dict, right_dict):
        """
        Check whether the left dictionary is a subset of the right dictionary.
        Args:
            left_dict (dict): dict
            right_dict (dict): dict

        Return:
            value (bool)
        """
        for left_key, left_value in left_dict.items():
            if left_key in right_dict.keys() and right_dict[left_key] == left_value:
                return True
        return False

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value (bool)

        Raise:
            ExpressionError
        """
        left_dict = self.left_element.calculate(data_backpack)
        right_dict = self.right_element.calculate(data_backpack)
        ret = self._judge_member(left_dict, right_dict)
        if self.sign == 'in':
            return ret
        if self.sign == 'notin':
            return not ret
        raise ExpressionError("Invalid sign %s " % self.sign)


class Unary(Expression):
    """
    Unary operation expression

    Attribute:
        sign (str): operator sign
        expression (Expression/Number) : expression
        _fields (list): member list
    """

    def __init__(self, sign, expression):
        """
        Constructor
        Args:
            sign (str): operator sign
            expression (Expression/Number) : expression
        """
        super().__init__()
        self._fields = ['sign', 'expression']
        self.sign = sign
        self.expression = expression

    @staticmethod
    def _get_operator_function(op_sign):
        """
        Get operator function from sign
        Args:
            op_sign (str): operator sign

        Returns:
            operator function
        """
        return {
            '+': operator.pos,
            '-': operator.neg,
            '!': operator.not_,
            '~': operator.invert,
        }[op_sign]

    def calculate(self, data_backpack):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value (bool)

        Raise:
            ExpressionError
        """
        value = self.expression.calculate(data_backpack)
        if value is None:
            raise ExpressionError("Invalid value %s " % value)
        operator_func = self._get_operator_function(self.sign)

        return operator_func(value)


class TimeFilter(Expression):
    """
    TimeFilter of function

    Attribute:
        num (int): num of time
        unit (str) : unit
        _fields (list): member list
    """

    def __init__(self, num, unit):
        """
        Constructor
        Args:
            num (Number): num of time
            unit (str) : unit
        """
        super().__init__()
        self._fields = ['num', 'unit']
        self.num = num
        self.unit = unit

    def calculate(self, data_backpack=None):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value (int)

        Raise:
            ExpressionError
        """
        num = ast.literal_eval(self.num)
        if self.unit == 'm':
            return num * 60
        if self.unit == 's':
            return num
        if self.unit == 'h':
            return num * 3600
        raise ExpressionError("TimeFilter calculate invalid unit %s " % self.unit)


class NumFilter(Expression):
    """
    NumFilter of function

    Attribute:
        num (int): num of time
        _fields (list): member list
    """

    def __init__(self, num):
        """
        Constructor
        Args:
            num (str): num of time
        """
        super().__init__()
        self._fields = ['num']
        self.num = num.lstrip("#")

    def calculate(self, data_backpack=None):
        """
        Calculate the expression
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value (int)

        """
        num = ast.literal_eval(self.num)
        return num


class FunctionCall(Expression):
    """
    FunctionCall

    Attribute:
        _fields (list): member list
        function_list (set): function list
        name (str): function name
        arguments (list): argument list
        func_class (ast.FunctionDef): built-in function
        target (str): data target
    """

    function_list = dict()

    def __init__(self, name, arguments=None, target="default"):
        """
        Constructor
        Args:
            name (str): function name
            arguments (list): argument list
            target (str/Name): data target
        """
        super().__init__()
        self._fields = ['name', 'arguments', 'target', 'func_class']
        if arguments is None:
            arguments = []
        self.name = "builtin_{}".format(name)
        self.arguments = arguments
        self.func_class = None
        if isinstance(target, Name):
            target = target.value
        self.target = target

    @staticmethod
    def get_function_list():
        """
        Get built in function list in builtin_function.py

        Return:
            None
        """
        function_file_path = os.path.join(CURRENT_PATH, "builtin_function.py")
        with open(function_file_path, "r") as file:
            tree = ast.parse(file.read())
            for func in tree.body:
                if isinstance(func, ast.FunctionDef) and func.name.startswith("builtin_"):
                    FunctionCall.function_list[func.name] = getattr(builtin_function, func.name)

    def calculate(self, data_backpack):
        """
        Calculate the function
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raises:
            ExpressionError
        """
        self.func_class = FunctionCall.function_list.get(self.name)
        if not self.func_class:
            raise ExpressionError("func_class is none ")
        return self.func_class(self.target, self.arguments, data_backpack)


class Literal(SourceElement):
    """
    Literal

    Attribute:
        _fields (list): member list
        value (str): value
        type (str): value type
    """

    def __init__(self, token):
        """
        Constructor
        Args:
            token (Token): token str
        """
        super().__init__()
        self._fields = ['value', 'type']
        self.value = token.slice[1].value
        self.type = token.slice[1].type

    def calculate(self, data_backpack=None):
        """
        Calculate the function
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value

        Raise:
            ExpressionError
        """
        if self.type in ('NUM', 'CHAR_LITERAL', 'STRING_LITERAL', 'SCI_NUM'):
            return ast.literal_eval(self.value)
        if self.type in ('TRUE', 'FALSE'):
            return bool(self.value.lower() == 'true')
        if self.type == "NULL":
            return None
        raise ExpressionError("Unknown Literal type")


class Pair(SourceElement):
    """
    Pair element

    Attribute:
        _fields (list): member list
        value (str): value
        key (str): key
        type (type): value type
    """

    def __init__(self, key, value):
        """
        Constructor
        Args:
            value (expression): value
            key (expression): key
        """
        super().__init__()
        self._fields = ['key', 'value', 'type']
        self.key = key
        self.value = value
        self.type = type(self)

    def calculate(self, data_backpack):
        """
        Calculate the function
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            dict
        """
        key = self.key.calculate(data_backpack)
        value = self.value.calculate(data_backpack)
        return {key: value}


class Dict(SourceElement):
    """
    Dict element

    Attribute:
        _fields (list): member list
        pair_list (list): pair list in dict
        type (type): value type
    """

    def __init__(self, pair_list=None):
        """
        Constructor
        Args:
            pair_list (list): value
        """
        super().__init__()
        self._fields = ['pair_list', 'type']
        if pair_list is None:
            self.pair_list = []
        self.pair_list = pair_list
        self.type = type(self)

    def calculate(self, data_backpack):
        """
        Calculate the function
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            dict
        """
        ret_dict = {}
        for pair in self.pair_list:
            real_pair = pair.calculate(data_backpack)
            ret_dict.update(real_pair)
        return ret_dict


class Name(SourceElement):
    """
    Name element

    Attribute:
        _fields (list): member list
        value (list): Value of name
        type (type): value type
    """

    def __init__(self, value):
        """
        Constructor
        Args:
            value (str): value
        """
        super().__init__()
        self._fields = ['value', 'type']
        self.value = value
        self.type = type(self)

    def calculate(self, data_backpack):
        """
        Calculate Name
        Args:
            data_backpack (DataBackpack): data cache

        Return:
            value
        """
        real_value = self.get_real_value(self.value, data_backpack)
        return real_value


FunctionCall.get_function_list()
