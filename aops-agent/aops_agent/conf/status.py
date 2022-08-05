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
SUCCESS = 200
FILE_CORRUPTED = 202
PARTIAL_SUCCEED = 206
FILE_NOT_FOUND = 410
PARAM_ERROR = 400
CONFLICT_ERROR = 409
HTTP_CONNECT_ERROR = 1001
UNKNOWN_ERROR = 1002


class StatusCode:
    """
    status code with related message
    """
    mapping = {
        SUCCESS: {
            'msg': 'operate success'
        },
        FILE_CORRUPTED: {
            'msg': 'file structure corrupted'
        },
        PARTIAL_SUCCEED: {
            'msg': 'request partial succceed'
        },
        FILE_NOT_FOUND: {
            'msg': 'file not found'
        },
        PARAM_ERROR: {
            'msg': 'parameter error'
        },
        HTTP_CONNECT_ERROR: {
            'msg': 'url connection error'
        },
        UNKNOWN_ERROR: {
            "msg": "unknown error"
        }
    }

    @classmethod
    def make_response_body(cls, code) -> dict:
        """
        make response body from mapping

        Args:
            code (int)

        Returns:
            dict: response body
        """
        message = cls.mapping.get(code) or cls.mapping.get(UNKNOWN_ERROR)
        response_body = {
            "msg": message.get("msg"),
        }
        return response_body