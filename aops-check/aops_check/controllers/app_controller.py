#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
import uuid
from typing import Dict, Tuple
from flask import jsonify

from aops_utils.database.helper import operate
from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import SUCCEED

from aops_check.conf import configuration
from aops_check.database.dao.app_dao import AppDao
from aops_check.utils.schema.app import (
    CreateAppSchema,
    QueryAppListSchema,
    QueryAppSchema
)


class CreateApp(BaseResponse):
    """
    Create app interface, it's a post request.
    """

    @staticmethod
    def _handle(args: Dict) -> Tuple[int, Dict[str, str]]:
        """
        1.generate uuid
        2.insert into database
        """
        result = {}
        app_id = str(uuid.uuid1()).replace('-', '')
        args['app_id'] = app_id
        status = operate(AppDao(configuration), args, 'create_app')
        if status == SUCCEED:
            result['app_id'] = app_id

        return status, result

    def post(self):
        """
        It's post request, step:
            1.verify token;
            2.verify args;
            3.generate uuid
            4.insert into database
        """
        return jsonify(self.handle_request(CreateAppSchema, self))


class QueryAppList(BaseResponse):
    """
    Query app list interface, it's a get request.
    """

    def get(self):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.insert into database
        """
        return jsonify(self.handle_request_db(QueryAppListSchema,
                                              AppDao(configuration),
                                              'query_app_list'))


class QueryApp(BaseResponse):
    """
    Query app interface, it's a get request.
    """

    def get(self):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.insert into database
        """
        return jsonify(self.handle_request_db(QueryAppSchema,
                                              AppDao(configuration),
                                              "query_app"))
