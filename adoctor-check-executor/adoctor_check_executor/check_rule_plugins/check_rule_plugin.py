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
Date: 2021/8/20 14:50
docs: check_rule_plugin.py
description: check rule plugin
"""

from abc import ABC, abstractmethod


class CheckRulePlugin(ABC):
    """
    Check rule plugin base

    Attributes:
        plugin_manager
    """

    def __init__(self):
        """
        Constructor
        """
        self.plugin_manager = None

    @abstractmethod
    def judge_condition(self, index, data_vector, main_data_name):
        """
        Judge the condition
        """

    def set_plugin_manager(self, plugin_manager):
        """
        Set plugin manager
        Args:
            plugin_manager (CheckRuleManager): check rule plugin manager

        Returns:
            None

        """
        self.plugin_manager = plugin_manager
