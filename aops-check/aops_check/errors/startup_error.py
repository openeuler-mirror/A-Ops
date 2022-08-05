#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Time:
Author:
Description:
"""
from typing import List


class StartupError(Exception):
    """
    It's an error that check server may raise when it's starting up.
    """
    __slots__ = ["__check_mode", "__support_mode"]

    def __init__(self, check_mode: str, support_mode: List[str]):
        self.__check_mode = check_mode
        self.__support_mode = support_mode

    @property
    def check_mode(self) -> str:
        return self.__check_mode

    @property
    def support_mode(self) -> list:
        return self.__support_mode

    def __str__(self):
        return "Check module's mode should be in %s, not %s" % (self.__support_mode, self.__check_mode)
