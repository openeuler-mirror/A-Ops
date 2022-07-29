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
Description: Restful APIs for host
"""
from typing import Dict, Tuple
from flask import jsonify

from aops_utils.restful.status import SUCCEED, DATABASE_CONNECT_ERROR, NO_DATA, TOKEN_ERROR
from aops_utils.restful.response import BaseResponse
from aops_utils.database.helper import operate
from aops_utils.database.table import User
from aops_utils.log.log import LOGGER
from aops_manager.database.proxy.host import HostProxy, HostInfoProxy
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.conf import configuration
from aops_manager.database import SESSION
from aops_manager.account_manager.cache import UserCache
from aops_manager.function.verify.host import (
    HostSchema,
    DeleteHostSchema,
    GetHostSchema,
    AddHostGroupSchema,
    DeleteHostGroupSchema,
    GetHostGroupSchema,
    GetHostInfoSchema
)


class AddHost(BaseResponse):
    """
    Interface for add host.
    Restful API: post
    """
    proxy = ""

    def _verify_user(self, username: str, password: str) -> Tuple[int, str]:
        # query from cache first
        user = UserCache.get(username)
        if user is None:
            LOGGER.error("no such user")
            return NO_DATA, ""

        res = User.check_hash_password(user.password, password)
        if not res:
            LOGGER.error("wrong username or password.")
            return TOKEN_ERROR, ""

        return SUCCEED, user.token

    def _handle(self, args: Dict) -> Tuple[int, Dict]:
        self.proxy = HostProxy()
        if not self.proxy.connect(SESSION):
            return DATABASE_CONNECT_ERROR, {}

        status_code, token = self._verify_user(
            args['username'], args.pop('password'))
        if status_code != SUCCEED:
            return status_code, {}

        status_code = self.proxy.add_host(args)
        if status_code == SUCCEED:
            return status_code, {"token": token}

        return status_code, {}

    def post(self):
        """
        Add host

        Args:
             (list)
            key (str)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(HostSchema, self, need_token=False, debug=False))


class DeleteHost(BaseResponse):
    """
    Interface for delete host.
    Restful API: DELETE
    """
    @staticmethod
    def _delete_host_vars(host_list, result):
        """
        Since the hosts have been deleted, the related host vars are need deleted too.

        Args:
            host_list (list): list of host which has been deleted successfully
            result (dict): response body from database proxy
        """
        host_name_list = []
        host_info = result.pop('host_info')
        for host_id in host_list:
            host_name_list.append(host_info[host_id])
        inventory = InventoryBuilder()
        inventory.remove_specified_host_vars(
            host_name_list, configuration.manager['HOST_VAULT_DIR'])

    def _handle(self, args):
        """
        Handle function

        Args:
            args (dict)

        Returns:
            int: status code
            dict: response body
        """
        proxy = HostProxy()
        if not proxy.connect(SESSION):
            return DATABASE_CONNECT_ERROR, {}

        status_code, result = proxy.delete_host(args)
        succeed_list = result.get('succeed_list')
        if status_code == SUCCEED and succeed_list:
            self._delete_host_vars(succeed_list, result)

        return status_code, result

    def delete(self):
        """
        Delete host

        Args:
            host_list (list): host id list

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(DeleteHostSchema, self))


class GetHost(BaseResponse):
    """
    Interface for get host.
    Restful API: POST
    """

    def post(self):
        """
        Get host

        Args:
            host_group_list (list): host group name list
            management (bool): whether it's a manage node
            sort (str): sort according to specified field
            direction (str): sort direction
            page (int): current page
            per_page (int): count per page

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(GetHostSchema,
                                              HostProxy(),
                                              'get_host',
                                              SESSION))


class GetHostCount(BaseResponse):
    """
    Interface for get host count.
    Restful API: POST
    """

    def post(self):
        """
        Get host

        Args:

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(None,
                                              HostProxy(),
                                              'get_host_count',
                                              SESSION))


class AddHostGroup(BaseResponse):
    """
    Interface for add host group.
    Restful API: POST
    """

    def post(self):
        """
        Add host group

        Args:
            host_group_name (str): group name
            description (str): group description

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(AddHostGroupSchema,
                                              HostProxy(),
                                              'add_host_group',
                                              SESSION))


class DeleteHostGroup(BaseResponse):
    """
    Interface for delete host group.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete host group

        Args:
            host_group_list (list): group name list

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(DeleteHostGroupSchema,
                                              HostProxy(),
                                              'delete_host_group',
                                              SESSION))


class GetHostGroup(BaseResponse):
    """
    Interface for get host group.
    Restful API: POST
    """

    def post(self):
        """
        Get host group

        Args:
            sort (str): sort according to specified field
            direction (str): sort direction
            page (int): current page
            per_page (int): count per page

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(GetHostGroupSchema,
                                              HostProxy(),
                                              'get_host_group',
                                              SESSION))


class GetHostInfo(BaseResponse):
    """
    Interface for get host info.
    Restful API: POST
    """
    @staticmethod
    def _handle(args):
        """
        Handle function

        Args:
            args (dict): request parameter

        Returns:
            tuple: (status code, result)
        """
        basic = args.get('basic')
        if not basic:
            return operate(HostInfoProxy(configuration), args, 'get_host_info')
        return operate(HostProxy(), args, 'get_host_info', SESSION)

    def post(self):
        """
        Get host info

        Args:
            host_list (list): host id list
            basic (bool)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(GetHostInfoSchema, self))
