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
Description: LRU cache, it's implemented by OrderDict
"""
from collections import OrderedDict
import threading


class LRUCache:
    """
    Base class of LRU cache, user needs to extend from the class to implement specific
    info cache.
    """
    def __init__(self, capacity):
        """
        Args:
            capacity (int): capacity of the cache
        """
        self.capacity = capacity
        self.queue = OrderedDict()
        self.mutex = threading.Lock()

    def get(self, key):
        """
        Get value from the cache according to the key and put the key
        to the front of the queue.

        Args:
            key (str)

        Returns:
            object
        """
        if key not in self.queue:
            return None

        with self.mutex:
            value = self.queue.pop(key)
            self.queue[key] = value

        return value

    def put(self, key, value):
        """
        Insert (key, value) to the cache.

        Args:
            key (str)
            value (object)
        """
        with self.mutex:
            if key in self.queue:
                self.queue.pop(key)
            elif len(self.queue) == self.capacity:
                self.queue.popitem(last=False)

            self.queue[key] = value
