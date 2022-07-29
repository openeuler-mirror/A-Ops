#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
Description: The implementation of Singleton class.
"""

import threading


class Singleton(type):
    """
    The singleton class to initialize a singleton object.
    """
    _instance_lock = threading.Lock()

    def __init__(cls, *args, **kwargs):
        """The singleton base class initializer"""
        cls._instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        """
        Writes classes where the instances behave like functions
        and can be called like a function
        """
        if cls._instance is None:
            with Singleton._instance_lock:
                if cls._instance is None:
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
