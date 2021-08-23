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
Time:
Author:
Description: Store key related to user
"""
import threading


class HostKey:
    """
    class HostKey is the cache the store key related to user .
    """
    _instance_lock = threading.Lock()
    mutex = threading.Lock()
    init_flag = False
    keys = {}
    key = ""

    def __new__(cls):
        """
        singleton class
        """
        if not hasattr(HostKey, "_instance"):
            with HostKey._instance_lock:
                if not hasattr(HostKey, "_instance"):
                    HostKey._instance = object.__new__(cls)

        return HostKey._instance

    def __init__(self):
        """
        Class instance initialization.
        """
        if HostKey.init_flag:
            return
        HostKey.keys = {}
        HostKey.init_flag = True

    @classmethod
    def update(cls, access_token, key):
        """
        Update key

        Args:
            access_token(str): user login token
            key(str)
        """
        HostKey.mutex.acquire()
        HostKey.keys[access_token] = key
        HostKey.key = key
        HostKey.mutex.release()

    @classmethod
    def delete(cls, access_token):
        """
        Update key

        Args:
            access_token(str): user login token
        """
        HostKey.mutex.acquire()
        HostKey.keys.pop(access_token)
        HostKey.mutex.release()

    @classmethod
    def get(cls, access_token):
        """
        Update key

        Args:
            access_token(str): user login token

        Returns:
            str
        """
        HostKey.mutex.acquire()
        key = HostKey.keys.get(access_token)
        HostKey.mutex.release()
        return key
