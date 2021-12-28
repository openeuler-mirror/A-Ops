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
Description: Restful APIs for user
"""
from aops_utils.database.helper import SESSION
from aops_manager.account_manager.database.proxy.account import UserDatabase
from aops_utils.restful.resource import BaseResource
from aops_manager.function.verify.acount import LoginSchema, ChangePasswordSchema, CertificateSchema, AddUserSchema


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
        return self.restful_result('add_user', UserDatabase(), AddUserSchema, SESSION)


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
        return self.restful_result('login', UserDatabase(), LoginSchema, SESSION)


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
        return self.restful_result('change_password', UserDatabase(), ChangePasswordSchema, SESSION)


class Certificate(BaseResource):
    """
    Interface for user certificate.
    Restful API: post
    """

    def post(self):
        """
        Certificate  user

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        return self.restful_result('certificate', UserDatabase(), CertificateSchema, SESSION)
