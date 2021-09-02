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

import unittest
from adoctor_diag_executor.function.calculation import calculate


class TestCalculation(unittest.TestCase):

    def test_expression_1(self):
        value_dict = {'a': True,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("a || b || c", value_dict), True)

    def test_expression_2(self):
        value_dict = {'a': True,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("a || b && c", value_dict), False)

    def test_expression_3(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': True
                      }
        self.assertEqual(calculate("a && b || c", value_dict), True)

    def test_expression_4(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': True
                      }
        self.assertEqual(calculate("a && (b || c)", value_dict), False)

    def test_expression_5(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("!a || b || c", value_dict), True)

    def test_expression_6(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("a || !b || c", value_dict), True)

    def test_expression_7(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("a || !(b || c)", value_dict), True)

    def test_expression_8(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("!(a || !(b || c))", value_dict), False)

    def test_expression_9(self):
        value_dict = {'a': False,
                      'b': False,
                      'c': False
                      }
        self.assertEqual(calculate("!(a && !(b || c))", value_dict), True)
