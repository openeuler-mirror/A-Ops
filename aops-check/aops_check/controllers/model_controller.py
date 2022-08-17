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
from flask import jsonify

from aops_utils.restful.response import BaseResponse
from aops_check.database import SESSION
from aops_check.database.dao.model_dao import ModelDao
from aops_check.utils.schema.model import QueryModelListSchema


class QueryModelList(BaseResponse):
    """
    Query model list interface, it's a post request.
    """

    def post(self):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.get model list from database
        """
        return jsonify(self.handle_request_db(QueryModelListSchema,
                                              ModelDao(),
                                              "get_model_list", SESSION))
