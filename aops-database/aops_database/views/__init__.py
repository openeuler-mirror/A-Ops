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
Description: Basic resource class
"""
from flask import jsonify
from flask import request
from flask_restful import Resource

from aops_utils.restful.status import make_response
from aops_utils.database.helper import operate


class BaseResource(Resource):
    """
    Offer a common action function
    """
    @staticmethod
    def do_action(action, proxy, session=None):
        """
        Do operate and get response

        Args:
            action(str): function name
            proxy(instance): API instance
            session(session or None): some database use session

        Returns:
            dict: response body
        """
        args = request.get_json()
        status_code = operate(proxy, args, action, session)
        response = make_response(status_code)
        return jsonify(response)
