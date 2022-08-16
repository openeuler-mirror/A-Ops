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


class Register:
    """
    It's a base register class which realizes register function.
    """

    def __init__(self):
        self.dict = {}

    def register(self, target: str) -> 'add':
        def add(key, value):
            self.dict[key] = value
            return value

        if callable(target):
            raise ValueError("register by method call is not support")

        return lambda x: add(target, x)

    def build(self, name: str) -> 'Register':
        return self.dict[name]

    @staticmethod
    def run():
        ...
