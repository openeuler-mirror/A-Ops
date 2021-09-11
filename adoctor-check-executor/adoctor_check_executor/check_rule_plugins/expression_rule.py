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
docs: expression_rule.py
description: expression rule
"""
from adoctor_check_executor.check_rule_plugins.check_rule_plugin import CheckRulePlugin
from adoctor_check_executor.check_rule_plugins.expression_parser.parser import Parser
from adoctor_check_executor.check_rule_plugins.expression_parser.visitor import ShiftVisitor
from adoctor_check_executor.check_rule_plugins.expression_parser.data_backpack import DataBackpack
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.common.check_error import CheckPluginError, \
    CheckItemError, CheckExceptionList
from aops_utils.log.log import LOGGER


class ExpressionCheckRule(CheckRulePlugin):
    """
    Keyword Check Rule
    """

    def __init__(self):
        """
        Constructor

        Raises:
            CheckPluginError
        """
        super().__init__()
        try:
            self._expression_parser = Parser()
            self._visitor = ShiftVisitor()
        except CheckExceptionList as exp:
            LOGGER.error("Get expression parser and shift visitor failed.")
            raise CheckPluginError from exp
        self.name = "expression_rule_plugin"
        self._syntax_tree = None
        self.time_shift = 0

    def analysis_expression(self, condition_str):
        """
        Analysis expression
        Args:
            condition_str: condition

        Returns:
            None

        """
        self._syntax_tree = self._expression_parser.parse_string(condition_str)
        self._syntax_tree.traverse(self._visitor)
        self._get_time_shift()

    def _get_time_shift(self):
        """
        Get time shift of expression

        Returns:
            time shift (int)

        """
        num_time_shift = executor_check_config.executor.get(
            "SAMPLE_PERIOD") * self._visitor.num_shift
        self.time_shift = max(num_time_shift, self._visitor.time_shift)
        LOGGER.debug("Get time shift is %s", self.time_shift)

    def judge_condition(self, index, data_vector, main_data_name):
        """
        Judge the condition is matched
        Args:
            index (int): the data item list to be checked
            data_vector (dict): check item
            main_data_name (str): main data name

        Returns:
            True-matched;False-unmatched

        Raises:
            CheckPluginError
        """
        data_backpack = DataBackpack(main_data_name, index, data_vector)
        if not self._syntax_tree:
            raise CheckItemError("syntax tree is None")
        ret = self._syntax_tree.calculate(data_backpack)
        return ret
