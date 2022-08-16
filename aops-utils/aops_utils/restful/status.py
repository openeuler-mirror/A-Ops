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
Description: Status code
"""

SUCCEED = 200
PARTIAL_SUCCEED = 206
SERVER_ERROR = 500
PARAM_ERROR = 1000
HTTP_CONNECT_ERROR = 1001
UNKNOWN_ERROR = 1002
DATABASE_CONNECT_ERROR = 1101
DATABASE_INSERT_ERROR = 1102
DATABASE_DELETE_ERROR = 1103
DATABASE_QUERY_ERROR = 1104
DATA_EXIST = 1105
DATA_DEPENDENCY_ERROR = 1106
DATABASE_UPDATE_ERROR = 1107
NO_DATA = 1108
WRONG_DATA = 1109
LOGIN_ERROR = 1200
TOKEN_ERROR = 1201
REPEAT_LOGIN = 1202
KEY_ERROR = 1203
CHANGE_PASSWORD = 1204
REPEAT_PASSWORD = 1205
CHANGE_PASSWORD_FAIL = 1206
TASK_EXECUTION_FAIL = 1301
REPEAT_TASK_EXECUTION = 1302
SET_AGENT_PLUGIN_STATUS_FAILED = 1401
WORKFLOW_ASSIGN_MODEL_FAIL = 1501


class StatusCode:  # pylint: disable=R0903
    """
    status code and related message.
    """
    mappings = {
        SUCCEED: {
            "msg": "operation succeed"
        },
        SERVER_ERROR: {
            "msg": "internal server error"
        },
        UNKNOWN_ERROR: {
            "msg": "unknown error"
        },
        HTTP_CONNECT_ERROR: {
            "msg": "restful connection error"
        },
        DATABASE_CONNECT_ERROR: {
            "msg": "connect to database error"
        },
        DATABASE_INSERT_ERROR: {
            "msg": "insert data into database fail"
        },
        DATABASE_DELETE_ERROR: {
            "msg": "delete data from database fail"
        },
        DATABASE_QUERY_ERROR: {
            "msg": "query data from database fail"
        },
        DATABASE_UPDATE_ERROR: {
            "msg": "update data in database fail"
        },
        DATA_EXIST: {
            "msg": "data has existed"
        },
        NO_DATA: {
            "msg": "No data found in database"
        },
        DATA_DEPENDENCY_ERROR: {
            "msg": "delete fail for it has dependency"
        },
        PARTIAL_SUCCEED: {
            "msg": "partial succeed"
        },
        LOGIN_ERROR: {
            "msg": "incorrect username or password"
        },
        TOKEN_ERROR: {
            "msg": "the session is invalid"
        },
        REPEAT_LOGIN: {
            "msg": "user has logined, repeat login"
        },
        KEY_ERROR: {
            "msg": "missing or invalid vault password, please certificate the vault password"
        },
        CHANGE_PASSWORD: {
            "msg": "please change the default password or you can not use"
        },
        REPEAT_PASSWORD: {
            "msg": "the new password is same as old password, change fail"
        },
        CHANGE_PASSWORD_FAIL: {
            "msg": "change password fail"
        },
        PARAM_ERROR: {
            "msg": "request parameter error"
        },
        TASK_EXECUTION_FAIL: {
            "msg": "Task execution failed."
        },
        WRONG_DATA: {
            "msg": "The query parameter is not valid, please check again"
        },
        REPEAT_TASK_EXECUTION: {
            "msg": "Task execute repeatedly"
        },
        WORKFLOW_ASSIGN_MODEL_FAIL: {
            "msg": "An error occurred when assign model to the workflow."
        },
        SET_AGENT_PLUGIN_STATUS_FAILED: {
            "msg": "Set agent plugin status failed"
        }
    }

    @classmethod
    def make_response(cls, code):
        """
        get response body from existed label mappings.

        Args:
            code(int): status code

        Returns:
            dict: response body
        """
        info = cls.mappings.get(code) or cls.mappings.get(UNKNOWN_ERROR)
        response_body = {
            "msg": info.get("msg"),
            "code": code
        }

        return response_body


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
