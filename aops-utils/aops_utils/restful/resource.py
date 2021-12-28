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
Time: 2021-12-23 10:34:01
Author: peixiaochao
Description: 
"""
import secrets

from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import make_response, SUCCEED, StatusCode, CHANGE_PASSWORD, \
    DATABASE_CONNECT_ERROR  # 暂时不换这个方法


class BaseResource(Resource):
    """
    Offer a common action function
    """

    @staticmethod
    def restful_result(action, proxy, schema, args=None, session=None, func="_handler"):
        """
        Do operate and get response

        Args:
            action(str): function name
            proxy(instance): API instance
            schema(instance): verify instance
            args(dict): request data
            session(session or None): some database use session
            func (str, optional): name of handle function. Defaults to '_handler'

        Returns:
            dict: response body
        """
        if args is None:
            args = BaseResource.request_data(request)
        access_token = request.headers.get('access_token')
        # redirect to login view ...
        if access_token is None:
            return getattr(BaseResource, func)(action, proxy, schema, args, session)

        verify_code = MyResponse.verify_all(
            args, schema, access_token)
        response = BaseResource.verify_comm(verify_code, proxy, args, action, session)
        return jsonify(response)

    @staticmethod
    def verify_comm(verify_code, proxy, args, action, session):
        """
        verify handler common

        Args:
            verify_code(int): status code
            action(str): function name
            proxy(instance): API instance
            schema(instance): verify instance
            args(dict): request data
            session(session or None): some database use session

        Returns:
            dict: response body
        """
        if verify_code != SUCCEED:
            response = StatusCode.make_response(verify_code)
            return jsonify(response)

        restful_response = BaseResource.operate(proxy, args, action, session)
        response = BaseResource.make_response(restful_response)
        return response

    @staticmethod
    def operate(proxy, args, func, session=None):
        """
        Database operation

        Args:
            proxy(proxy instance)
            data(dict)
            func(str): function name
            session(session or None): some database use session

        Returns:
            int: status code
        """

        if session is not None:
            if not proxy.connect(session):
                return DATABASE_CONNECT_ERROR
        else:
            if not proxy.connect():
                return DATABASE_CONNECT_ERROR

        function = getattr(proxy, func)
        res = function(args)
        proxy.close()
        return res

    @staticmethod
    def request_data(req_data):
        """
        Parse request parameters
        Args:
            req_data : request data

        Returns:
            request body or args

        """
        if req_data.method == "GET":
            return req_data.args

        else:
            return req_data.get_json()

    @staticmethod
    def _handler(action, proxy, schema, args=None, session=None):
        """
        Do operate and get response

        Args:
            action(str): function name
            proxy(instance): API instance
            schema(instance): verify instance
            args(dict): request data
            session(session or None): some database use session

        Returns:
            dict: response body
        """
        verify_code = MyResponse.verify_args(args, schema)
        response = BaseResource.verify_comm(verify_code, proxy, args, action, session)

        if response['code'] in (SUCCEED, CHANGE_PASSWORD):
            # generate access token
            access_token = secrets.token_hex(16)
            response['access_token'] = access_token
        return jsonify(response)

    @staticmethod
    def make_response(res):
        """
        Make response according to status code

        Args:
            res(tuple or int): result, the first element is status code, and when res is tuple,
                                the second element is a dict that need to be addded to response

        Returns:
            dict: response body
        """
        if isinstance(res, tuple):
            response = StatusCode.make_response(res[0])
            response.update(res[1])
        else:
            response = StatusCode.make_response(res)

        return response
