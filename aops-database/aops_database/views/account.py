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
Description: Restful apis about account
"""
from aops_database.function.helper import SESSION
from aops_database.proxy.account import UserDatabase
from aops_database.views import BaseResource


class AddUser(BaseResource):
    """
    Interface for register user.
    Restful API: post
    """

    def post(self):
        """
        Add user

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        return self.do_action('add_user', UserDatabase(), SESSION)


class Login(BaseResource):
    """
    Interface for user login.
    Restful API: post
    """

    def post(self):
        """
        User login

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        return self.do_action('login', UserDatabase(), SESSION)


class ChangePassword(BaseResource):
    """
    Interface for user change password.
    Restful API: post
    """

    def post(self):
        """
        Change password

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        return self.do_action('change_password', UserDatabase(), SESSION)
