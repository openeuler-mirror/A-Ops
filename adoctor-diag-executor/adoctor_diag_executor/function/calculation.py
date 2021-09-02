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

import re
from adoctor_diag_executor.function.diag_exception import ExpressionError


def calculate(diag_expression, leaves_dict):
    """
    Calculate the diag_condition expression's value
    Args:
        diag_expression (str): String of the expression
        leaves_dict (dict): Dictionary of the leaves and their diagnostic results

    Returns:
        bool: Value of the expression
    """
    if not diag_expression or diag_expression.isspace():
        raise ExpressionError("Expression is empty.")

    # split expression by '&&', '||', '!', '(' and ')'. \\ is to escape the special characters.
    exp_list = re.split('(&&|\\|\\||!|\\(|\\))', diag_expression)

    stack = []
    left_num = None
    last_operation = None
    # has '!' in front or not
    not_sign = False

    for rough_exp in exp_list:
        exp = rough_exp.strip()
        if not exp:
            continue

        if exp in leaves_dict:
            right_num = leaves_dict[exp]
            right_num = _not_cal(not_sign, right_num)
            not_sign = False

            left_num = _and_or_cal(last_operation, left_num, right_num)
            last_operation = None

        elif exp in ('&&', '||'):
            if last_operation:
                raise ExpressionError("Double operators are used together.")
            last_operation = exp

        elif exp == '!':
            not_sign = True

        elif exp == '(':
            stack.append(left_num)
            stack.append(last_operation)
            stack.append(not_sign)
            left_num = None
            last_operation = None
            not_sign = False

        elif exp == ')':
            right_num = left_num
            try:
                not_sign = stack.pop()
                last_operation = stack.pop()
                left_num = stack.pop()
            except IndexError as error:
                raise ExpressionError("Parenthesis doesn't match correctly.") from error

            right_num = _not_cal(not_sign, right_num)
            not_sign = False

            left_num = _and_or_cal(last_operation, left_num, right_num)
            last_operation = None

        else:
            raise ExpressionError("Sub node '%s' doesn't match the nodes in ForkList." % exp)

    if stack:
        raise ExpressionError("Parenthesis doesn't match correctly.")

    return left_num


def _and_or_cal(opr, left, right):
    """
    calculate two number with operation "&&" or "||"
    Args:
        opr (str): operation
        left (bool): left number
        right (bool): right number
    Raises:
        ExpressionError
    Returns:
        bool: expression value
    """
    if opr == '&&':
        if left is None or right is None:
            raise ExpressionError("&& operation should have two parameters.")
        ans = left and right
    elif opr == '||':
        if left is None or right is None:
            raise ExpressionError("|| operation should have two parameters.")
        ans = left or right
    else:
        # last operation is None, return b directly
        ans = right
    return ans


def _not_cal(not_sign, right):
    """
    Reverse number
    Args:
        not_sign (bool): if has not sign
        right (bool): right number

    Returns:
        bool
    """
    if not_sign:
        right = not right
    return right
