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

from aops_check.errors.startup_error import StartupError


class Mode:
    """
    It's a base mode class which realizes register function for check mode.
    """
    def __init__(self):
        self.__dict = {}

    def register(self, target: str) -> 'add':
        def add(key, value):
            self.__dict[key] = value
            return value

        if callable(target):
            raise ValueError("register by method call is not support")

        return lambda x: add(target, x)

    def build(self, name: str) -> 'Mode':
        if name not in self.supported_mode:
            raise StartupError(name, self.supported_mode)
        return self.__dict[name]

    @property
    def supported_mode(self) -> List[str]:
        return list(self.__dict.keys())

    @staticmethod
    def run():
        ...


mode = Mode()
