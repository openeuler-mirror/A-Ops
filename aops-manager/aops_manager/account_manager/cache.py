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
from typing import NoReturn
from dataclasses import dataclass

from aops_utils.database.table import User
from aops_utils.log.log import LOGGER
from aops_manager.database.proxy.account import UserProxy
from aops_manager.database import SESSION


@dataclass
class UserInfo:
    username: str
    password: str
    token: str


class UserCache:
    """
    class UserCache is the cache the store key related to user .
    """
    _instance_lock = threading.Lock()
    mutex = threading.Lock()
    init_flag = False
    cache = {}
    key = ""

    def __new__(cls):
        """
        singleton class
        """
        if not hasattr(UserCache, "_instance"):
            with UserCache._instance_lock:
                if not hasattr(UserCache, "_instance"):
                    UserCache._instance = object.__new__(cls)

        return UserCache._instance

    def __init__(self):
        """
        Class instance initialization.
        """
        if UserCache.init_flag:
            return
        UserCache.cache = {}
        UserCache.init_flag = True

    @classmethod
    def update(cls, key: str, user: User) -> NoReturn:
        """
        Update key

        Args:
            key: username
            user
        """
        UserCache.mutex.acquire()
        UserCache.cache[key] = UserInfo(
            user.username, user.password, user.token)
        UserCache.key = key
        UserCache.mutex.release()

    @classmethod
    def delete(cls, key: str) -> NoReturn:
        """
        remove key from cache
        """
        UserCache.mutex.acquire()
        UserCache.cache.pop(key)
        UserCache.mutex.release()

    @classmethod
    def get(cls, key: str) -> UserInfo:
        """
        Update key
        """
        UserCache.mutex.acquire()
        user = UserCache.cache.get(key)

        # need to query from database, and update cache
        if user is None:
            proxy = UserProxy()
            if proxy.connect(SESSION):
                query_res = proxy.session.query(
                    User).filter_by(username=key).all()
                if len(query_res) == 0:
                    LOGGER.error("no such user, please check username again.")
                    UserCache.mutex.release()
                    return user
                user = query_res[0]
                UserCache.cache[key] = UserInfo(
                    user.username, user.password, user.token)
                proxy.close()
            else:
                LOGGER.error("connect to database error, cannot get user token")

        UserCache.mutex.release()
        return user
