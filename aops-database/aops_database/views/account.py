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
from flask import request, jsonify
from flask_restful import Resource

from aops_database.function.helper import SESSION, operate
from aops_database.proxy.account import UserDatabase
from aops_utils.restful.status import make_response


class AddUser(Resource):
    """
    Interface for register user.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Add user

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        proxy = UserDatabase()
        action = 'add_user'
        response = make_response(operate(proxy, args, action, SESSION))

        return jsonify(response)


class Login(Resource):
    """
    Interface for user login.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        User login

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        proxy = UserDatabase()
        action = 'login'
        response = make_response(operate(proxy, args, action, SESSION))

        return jsonify(response)


class ChangePassword(Resource):
    """
    Interface for user change password.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Change password

        Args:
            username(str)
            password(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        proxy = UserDatabase()
        action = 'change_password'
        response = make_response(operate(proxy, args, action, SESSION))

        return jsonify(response)
