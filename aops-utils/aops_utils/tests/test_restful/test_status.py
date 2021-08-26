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
Description:
"""
import unittest

from aops_utils.restful.status import PARAM_ERROR, SUCCEED, StatusCode, make_response, UNKNOWN_ERROR


class TestStatus(unittest.TestCase):
    def test_restful_status_code(self):
        code = 1132131

        res = StatusCode.make_response(code)
        expected_res = StatusCode.make_response(UNKNOWN_ERROR)
        self.assertEqual(res["msg"], expected_res["msg"])

        code = PARAM_ERROR
        res = StatusCode.make_response(code)
        expected_res = StatusCode.make_response(PARAM_ERROR)
        self.assertEqual(res, expected_res)

    def test_restful_response(self):
        data = (SUCCEED, {"a": 1})
        res= make_response(data)
        expected_res = {
            "code": SUCCEED,
            "msg": "openration succeed",
            "a": 1
        }
        self.assertEqual(res, expected_res)

        data = (SUCCEED)
        res= make_response(data)
        expected_res = {
            "code": SUCCEED,
            "msg": "openration succeed"
        }
        self.assertEqual(res, expected_res)

