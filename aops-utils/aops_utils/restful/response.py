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
Description: response function
"""
import json
import requests
from flask import request, jsonify
from flask_restful import Resource

from aops_utils.log.log import LOGGER
from aops_utils.restful.serialize.validate import validate
from aops_utils.restful.status import HTTP_CONNECT_ERROR, PARAM_ERROR,\
    StatusCode, SERVER_ERROR, SUCCEED, TOKEN_ERROR, make_response
from aops_utils.database.helper import operate


class MyResponse:
    """
    response function
    """
    @classmethod
    def get_response(cls, method, url, data, header=None):
        """
        send a request and get the response

        Args:
            method(str): request method
            url(str): requset url
            data(dict): params in body
            header(dict): request header

        Returns:
            dict: response body
        """
        if not isinstance(data, dict):
            LOGGER.error("The param format of rest is not dict")
            result = StatusCode.make_response(PARAM_ERROR)
            return result

        try:
            if header:
                response = requests.request(
                    method=method, url=url, json=data, headers=header, timeout=600)
            else:
                response = requests.request(
                    method=method, url=url, json=data, timeout=600)
            if response.status_code != 200:
                result = StatusCode.make_response(SERVER_ERROR)
            else:
                result = json.loads(response.text)
        except requests.exceptions.ConnectionError as error:
            LOGGER.error(error)
            result = StatusCode.make_response(HTTP_CONNECT_ERROR)

        return result

    @classmethod
    def verify_args(cls, args, schema, load=False):
        """
        Verify restful args

        Args:
            args(dict): parameter to be verified
            schema(class): verifier
            load(bool): do parameter deserializing if load is set to true

        Returns:
            int: status code
        """
        # verify the params
        args, errors = validate(schema, args, load)
        if errors:
            LOGGER.error(errors)
            return PARAM_ERROR

        return SUCCEED

    @classmethod
    def verify_token(cls, token, args):
        """
        Verify token

        Args:
            token(str)
            args(dict)

        Returns:
            int: status code
        """
        # temp
        if token:
            args['username'] = "admin"
            return SUCCEED

        return TOKEN_ERROR

    @classmethod
    def verify_all(cls, args, schema, token, load=False):
        """
        Verify args and token

        Args:
            args(dict): parameter to be verified
            schema(class): verifier
            token(str)
            load(bool)

        Returns:
            int: status code
        """
        res = cls.verify_args(args, schema, load)
        if res != SUCCEED:
            return res
        res = cls.verify_token(token, args)

        return res

    @classmethod
    def get_result(cls, res, method, url, args):
        """
        Get response result

        Args:
            res(int): verify result
            method(str): restful function
            url(str): restful url
            args(dict): parameter

        Returns:
            dict: response body
        """
        if res == SUCCEED:
            response = cls.get_response(method, url, args)
        else:
            response = StatusCode.make_response(res)

        return response

    @classmethod
    def verify_request(cls, schema=None):
        """
        Get request args, verify token and parameter

        Args:
            schema (class, optional): parameter verifying schema. Defaults to None.

        Returns:
            dict: request args
            int: verify status code
        """
        if request.method == "GET":
            args = request.args.to_dict()
        else:
            args = request.get_json()

        LOGGER.debug(request.base_url)
        LOGGER.debug("Interface %s received args: %s", request.endpoint, args)

        access_token = request.headers.get('access_token')

        # when there is no need to verify parameter
        if schema is None:
            verify_res = cls.verify_token(access_token, args)
        else:
            verify_res = MyResponse.verify_all(
                args, schema, access_token)

        return args, verify_res

    @classmethod
    def get_db_response(cls, args, verify_res, proxy, action, session):
        """
        Operate database and get response of the restful request

        Args:
            args (dict): request args
            verify_res (int): verify status code
            proxy (class): database proxy class
            action (str): database proxy function
            session (scoped_session): mysql scoped_session object

        Returns:
            dict: response body
        """
        if verify_res != SUCCEED:
            return jsonify(make_response(verify_res))

        operate_res = operate(proxy, args, action, session)
        response = make_response(operate_res)
        return jsonify(response)


class BaseResponse(Resource):
    """
    Restful base class, offer a basic function that can handle the request.
    """
    @classmethod
    def get_response(cls, method, url, data, header=None):
        """
        send a request and get the response

        Args:
            method(str): request method
            url(str): requset url
            data(dict): params in body
            header(dict): request header

        Returns:
            dict: response body
        """
        if not isinstance(data, dict):
            LOGGER.error("The param format of rest is not dict")
            result = StatusCode.make_response(PARAM_ERROR)
            return result

        try:
            if header:
                response = requests.request(
                    method=method, url=url, json=data, headers=header, timeout=600)
            else:
                response = requests.request(
                    method=method, url=url, json=data, timeout=600)
            if response.status_code != 200:
                result = StatusCode.make_response(SERVER_ERROR)
            else:
                result = json.loads(response.text)
        except requests.exceptions.ConnectionError as error:
            LOGGER.error(error)
            result = StatusCode.make_response(HTTP_CONNECT_ERROR)

        return result

    @classmethod
    def make_response(cls, res):
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

    @classmethod
    def get_result(cls, res, method, url, args):
        """
        Get response result

        Args:
            res(int): verify result
            method(str): restful function
            url(str): restful url
            args(dict): parameter

        Returns:
            dict: response body
        """
        if res == SUCCEED:
            response = cls.get_response(method, url, args)
        else:
            response = StatusCode.make_response(res)

        return response

    @classmethod
    def verify_args(cls, args, schema, load=False):
        """
        Verify restful args

        Args:
            args(dict): parameter to be verified
            schema(class): verifier
            load(bool): do parameter deserializing if load is set to true

        Returns:
            int: status code
        """
        # verify the params
        args, errors = validate(schema, args, load)
        if errors:
            LOGGER.error(errors)
            return PARAM_ERROR

        return SUCCEED

    @classmethod
    def verify_token(cls, token, args):
        """
        Verify token

        Args:
            token(str)
            args(dict)

        Returns:
            int: status code
        """
        # temp
        if token:
            args['username'] = "admin"
            return SUCCEED

        return TOKEN_ERROR

    @classmethod
    def verify_all(cls, args, schema, token, load=False):
        """
        Verify args and token

        Args:
            args(dict): parameter to be verified
            schema(class): verifier
            token(str)
            load(bool)

        Returns:
            int: status code
        """
        res = cls.verify_args(args, schema, load)
        if res != SUCCEED:
            return res
        res = cls.verify_token(token, args)

        return res

    @classmethod
    def verify_request(cls, schema=None, need_token=True, debug=True):
        """
        Get request args, verify token and parameter

        Args:
            schema (class, optional): parameter verifying schema. Defaults to None.
            need_token (bool, optional): whether need to verify the token. Defaults to True.
            debug (bool, optional): whether need to print args and interface info. Defaults to True.

        Returns:
            dict: request args
            int: verify status code
        """
        if request.method == "GET":
            args = request.args.to_dict()
        else:
            args = request.get_json()

        if debug:
            LOGGER.debug(request.base_url)
            LOGGER.debug("Interface %s received args: %s", request.endpoint, args)

        access_token = request.headers.get('access_token')

        if schema is not None:
            verify_res = cls.verify_args(args, schema)
            if verify_res != SUCCEED:
                return args, verify_res

        if need_token:
            verify_res = cls.verify_token(access_token, args)

        return args, verify_res

    def handle_request(self, schema, obj, func='_handle', need_token=True, debug=True):
        """
        Get args and verify the args, then call the specific handle function.

        Args:
            schema (class): schema for verifying args.
            obj (class): class which used to get the handle function, which is a reflection.
            func (str, optional): name of handle function. Defaults to '_handle'.
            need_token (bool, optional): whether need to verify the token. Defaults to True.
            debug (bool, optional): whether need to print args and interface info. Defaults to True.

        Returns:
            dict: response body
        """
        args, status = self.verify_request(schema, need_token=need_token, debug=debug)
        if status == SUCCEED:
            status = getattr(obj, func)(args)

        return self.make_response(status)

    def handle_request_db(self, schema, proxy, func, session=None, debug=True):
        """
        Get args and verify the args, when the verify result is SUCCEED, query from the database
        according to proxy, func and session.

        Args:
            schema (class): schema for verifying args.
            proxy (class): database proxy class.
            func (str): database proxy function.
            session (scoped_session, optional): mysql scoped_session object. Default to None.
            debug (bool, optional): whether need to print args and interface info. Defaults to True.

        Returns:
            dict: response body
        """
        args, status = self.verify_request(schema, debug=debug)
        if status == SUCCEED:
            status = operate(proxy, args, func, session)

        return self.make_response(status)
