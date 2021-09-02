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
Date: 2021/8/7 19:50
docs: visitor.py
description: visitor of expression grammar tree
"""


class ShiftVisitor:
    """
    Visitor to get time or number shift

    Attributes:
        time_shift (int): get the max time shift
        num_shift (int): get the max num shift
    """

    def __init__(self):
        """
        Constructor
        """
        self.time_shift = 0
        self.num_shift = 0

    def visit_TimeFilter(self, time_filter):
        """
        Constructor
        Args:
            time_filter (TimeFilter): time filter

        Returns:
            None
        """
        self.time_shift = max(self.time_shift, time_filter.calculate())

    def visit_NumFilter(self, num_filter):
        """
        Constructor
        Args:
            num_filter (NumFilter): time filter

        Returns:
            None
        """
        self.num_shift = max(self.num_shift, num_filter.calculate())
