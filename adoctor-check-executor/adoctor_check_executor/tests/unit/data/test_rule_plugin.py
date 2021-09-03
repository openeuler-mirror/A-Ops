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


class TestCheckRule(CheckRulePlugin):
    """
    Keyword Check Rule
    """

    def __init__(self):
        super().__init__()
        self.name = "test_check_rule"

    def judge_condition(self, index, data_vector, main_data_name):
        """
        Judge the condition is matched
        Args:
            index (int): the data item list to be checked
            data_vector (dict): check item
            main_data_name (str): main data name

        Returns:
            True-matched;False-unmatched

        """
        print("Input index %s, data_vector %s, main_data_name %s" % (index, 
                                                                     data_vector,
                                                                     main_data_name))
        return True
