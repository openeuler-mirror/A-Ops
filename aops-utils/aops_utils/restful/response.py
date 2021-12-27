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

from aops_utils.log.log import LOGGER
from aops_utils.restful.serialize.validate import validate
from aops_utils.restful.status import HTTP_CONNECT_ERROR, PARAM_ERROR,\
    StatusCode, SERVER_ERROR, SUCCEED, TOKEN_ERROR


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
