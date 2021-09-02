#!/usr/bin/python3
# -*- coding:UTF=8 -*-
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
Date: 2021/8/31 10:30
docs: CheckItemManager.py
description: Check item manager
"""
import threading
import copy
from aops_utils.log.log import LOGGER
from aops_utils.singleton import singleton
from adoctor_check_executor.common.check_msg import CheckMsgToolKit
from adoctor_check_executor.common.check_error import CheckExceptionList
from adoctor_check_executor.check_executor.check_item import CheckItemDetail, CheckItem


@singleton
class CheckItemManager:
    """
    The manager of check item

    Attributes:
        _cache: cache of check item
        _check_item_lock: thread lock of _cache
    """

    def __init__(self):
        """
        Constructor
        """
        self._cache = dict()
        self._check_item_lock = threading.Lock()

    def query_check_rule(self):
        """
        Query check rule
        """
        user_list = CheckMsgToolKit.get_user_list_from_database()
        if not user_list:
            LOGGER.error("No user found.Cannot get check rule.")
        for user in user_list:
            check_items = CheckMsgToolKit.get_check_rule_from_database(user)
            if not check_items:
                LOGGER.info("No check items get for user %s", user)
                continue
            self.import_check_item(user, check_items)

    def _add_check_item(self, user, check_item_info):
        """
        Get check item in manager cache.
        If has been cached, return check item;
        If not, return a new check item object.
        Args:
            check_item_info (dict): check item info
            {
                "check_item": ""
                "data_list": [{
                    "name": "data1",
                    "type": "log",
                    "label":{
                        "key":"value"
                    }
                }]
                "check_condition": "",
                "check_result_description": "",
                "check_rule_plugin":""
            }
            user (str): user of the check item

        Returns:
            check item

        """

        try:
            check_item_detail = CheckItemDetail(user, check_item_info)
        except CheckExceptionList as exp:
            LOGGER.debug("Create check item detail failed %s, %s", check_item_info, exp)
            return

        if user not in self._cache:
            self._cache[user] = dict()
        if check_item_detail.check_item_name in self._cache.get(user):
            LOGGER.debug("Pop the old check item: %s", check_item_detail.check_item_name)
            self._cache.get(user).pop(check_item_detail.check_item_name)

        try:
            self._cache.get(user)[check_item_detail.check_item_name] = CheckItem(check_item_detail)
        except CheckExceptionList as exp:
            LOGGER.error("CheckItemError %s", exp)

    def clear(self, user):
        """
        Clear the cache in manager
        Args:
            user (str) : user to clear

        Returns:
            None

        """
        self._check_item_lock.acquire()
        if user in self._cache:
            self._cache.get(user).clear()
        self._check_item_lock.release()

    def get_check_item(self, user, check_item_name):
        """
        Get a check item copy from check item manager
        Args:
            user (str) : user to clear
            check_item_name (str) : check item

        Returns:
            None

        """
        self._check_item_lock.acquire()
        if user not in self._cache.keys():
            LOGGER.warning("Cannot find check item of user %s", user)
            self._check_item_lock.release()
            return None
        if check_item_name not in self._cache.get(user).keys():
            LOGGER.warning("Cannot find check item of check_item_name %s", check_item_name)
            self._check_item_lock.release()
            return None
        check_item = copy.deepcopy(self._cache.get(user).get(check_item_name))
        self._check_item_lock.release()
        return check_item

    def get_check_item_list(self, user):
        """
        Get check item list copy from check item manager
        Args:
            user (str) : user to clear

        Returns:
            None

        """
        self._check_item_lock.acquire()
        if user not in self._cache.keys():
            LOGGER.warning("Cannot find check item of user %s", user)
            self._check_item_lock.release()
            return None
        check_item_list = copy.deepcopy(self._cache.get(user))
        self._check_item_lock.release()
        return list(check_item_list.values())

    def import_check_item(self, user, check_item_list):
        """
        Import check item to check item list
        Args:
            user (str) : user to import
            check_item_list (list) : check item list

        Returns:
            None
        """
        self._check_item_lock.acquire()
        for check_item in check_item_list:
            self._add_check_item(user, check_item)
        self._check_item_lock.release()

    def delete_check_item(self, user, check_item_list):
        """
        Delete the check item cache in manager
        Args:
            user (str) : user to delete
            check_item_list (list) : check item list

        Returns:
            None
        """
        self._check_item_lock.acquire()
        if not check_item_list:
            LOGGER.warning("Delete check item list is null")
        else:
            if user not in self._cache:
                LOGGER.error("user not existed")
                self._check_item_lock.release()
                return
            for check_item in check_item_list:
                if check_item in self._cache.get(user).keys():
                    self._cache.get(user).pop(check_item)
                    LOGGER.debug("delete check item user %s check_item %s", user, check_item)
        self._check_item_lock.release()


check_item_manager = CheckItemManager()
