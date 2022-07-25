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
Description: Restful APIs for user
"""
import secrets
from typing import Dict
from flask import jsonify

from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import SUCCEED, CHANGE_PASSWORD, DATABASE_CONNECT_ERROR
from aops_utils.database.helper import operate
from aops_utils.database.table import User
from aops_manager.account_manager.cache import UserCache
from aops_manager.account_manager.key import HostKey
from aops_manager.database import SESSION
from aops_manager.database.proxy.account import UserProxy
from aops_manager.function.verify.acount import (
    LoginSchema,
    CertificateSchema,
    ChangePasswordSchema,
    AddUserSchema
)


class AddUser(BaseResponse):
    """
    Interface for register user.
    Restful API: post
    """

    def post(self):
        """
        Add user

        Args:
            username (str)
            password (str)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request_db(AddUserSchema,
                                              UserProxy(),
                                              'add_user',
                                              SESSION,
                                              False))


class Login(BaseResponse):
    """
    Interface for user login.
    Restful API: post
    """
    @staticmethod
    def _handle(args):
        result = {}
        status_code = operate(UserProxy(), args, 'login', SESSION)
        if status_code in (SUCCEED, CHANGE_PASSWORD):
            # generate access token
            access_token = secrets.token_hex(16)
            result['access_token'] = access_token
        return status_code, result

    def post(self):
        """
        User login

        Args:
            username (str)
            password (str)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(LoginSchema,
                                           self,
                                           need_token=False,
                                           debug=False))


class ChangePassword(BaseResponse):
    """
    Interface for user change password.
    Restful API: post
    """
    @staticmethod
    def _handle(args):
        proxy = UserProxy()
        if not proxy.connect(SESSION):
            return DATABASE_CONNECT_ERROR
        
        status_code, user = proxy.change_password(args)
        if status_code == SUCCEED:
            UserCache.update(user.username, user)

        return status_code

    def post(self):
        """
        Change password

        Args:
            password (str): new password

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(ChangePasswordSchema,
                                           self,
                                           debug=False))


class Certificate(BaseResponse):
    """
    Interface for user certificate.
    Restful API: post
    """
    @staticmethod
    def _handle(args):
        """
        Handle function

        Args:
            args (dict)

        Returns:
            int: status code
        """
        # save key
        HostKey.update(args['username'], args['key'])

        return SUCCEED

    def post(self):
        """
        Certificate  user

        Args:
            key (strs)

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(CertificateSchema, self, debug=False))
