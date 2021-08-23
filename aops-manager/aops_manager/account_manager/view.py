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
import secrets
from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_manager.account_manager.key import HostKey
from aops_manager.function.verify.acount import ChangePasswordSchema, LoginSchema, CertificateSchema
from aops_utils.conf.constant import DATA_USER_CHANGEPASSWORD, DATA_USER_LOGIN
from aops_utils.restful.status import CHANGE_PASSWORD, SUCCEED, StatusCode
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_datacenter_url


class Login(Resource):
    """
    Interface for login.
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
        database_url = make_datacenter_url(DATA_USER_LOGIN)
        verify_res = MyResponse.verify_args(args, LoginSchema)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        if response['code'] in (SUCCEED, CHANGE_PASSWORD):
            # generate access token
            access_token = secrets.token_hex(16)
            response['access_token'] = access_token

        return jsonify(response)


class ChangePassword(Resource):
    """
    Interface for change password.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Add host

        Args:
            password(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, ChangePasswordSchema, access_token)
        database_url = make_datacenter_url(DATA_USER_CHANGEPASSWORD)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class Certificate(Resource):
    """
    Interface for host certificate.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        User certificate

        Args:
            key(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, CertificateSchema, access_token)
        if verify_res == SUCCEED:
            # save key
            HostKey.update(access_token, args['key'])

        response = StatusCode.make_response(verify_res)
        return jsonify(response)
