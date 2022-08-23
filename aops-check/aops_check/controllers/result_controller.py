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
from flask import jsonify

from aops_check.database import SESSION
from aops_check.database.dao.result_dao import ResultDao
from aops_check.utils.schema.result import QueryCheckResultHostSchema, QueryCheckResultListSchema
from aops_utils.restful.response import BaseResponse


class QueryCheckResultHost(BaseResponse):
    """
        Interface for get check result.
        Restful API: GET
    """

    def get(self):
        """
            Get check result by alert id
        Returns:
            Response:
                {"code": int,
                "msg": "string",
                "result": {
                    "host id": {
                        "host_ip": "ip address",
                        "host_name": "string",
                        "is_root": false
                        "host_check_result":[{
                                "is_root": boolean,
                                "label": "string",
                                "metric_name": "string",
                                "time": time
                            }
                        ...
                        ]}}}
        """
        return jsonify(self.handle_request_db(QueryCheckResultHostSchema,
                                              ResultDao(),
                                              'query_result_host',
                                              SESSION))


class QueryCheckResultList(BaseResponse):
    """
        Interface for get check result list.
        Restful API: GET
    """
    def get(self):
        """
            get check result list from database
        """
        return jsonify(self.handle_request_db(QueryCheckResultListSchema,
                                              ResultDao(),
                                              'query_result_list',
                                              SESSION))
