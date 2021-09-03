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
Date: 2021/8/4 20:26
docs: check_error.py
description: check error
"""
from kafka.errors import KafkaError


class CheckExecutorError(Exception):
    """
    Self-defined Exception class of check executor
    """

    def __init__(self, error_info=''):
        super().__init__(self)
        self.message = error_info

    def __str__(self):
        return self.message


class CheckItemError(CheckExecutorError):
    """
    Self-defined Exception class of check item
    """


class ExpressionError(CheckExecutorError):
    """
    Self-defined Exception class of expression
    """


class ExpressionFunctionError(CheckExecutorError):
    """
    Self-defined Exception class of expression function
    """


class CheckPluginError(CheckExecutorError):
    """
    Self-defined Exception class of check plugin
    """


CheckExceptionList = (StopIteration, GeneratorExit, ZeroDivisionError, OverflowError,
                      AttributeError, EOFError, IOError, ImportError, IndexError,
                      KeyError, MemoryError, NameError, UnboundLocalError, ReferenceError,
                      RuntimeError, NotImplementedError, SyntaxError, IndentationError,
                      TabError, TypeError, ValueError, UnicodeDecodeError, UnicodeEncodeError,
                      SystemExit, ArithmeticError, FloatingPointError, AssertionError,
                      CheckItemError, CheckPluginError, ExpressionError,
                      ExpressionFunctionError, KafkaError)
