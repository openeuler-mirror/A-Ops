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
from marshmallow import Schema, fields

from aops_utils.restful.serialize.validate import validate

class Test(Schema):
    a = fields.String(required=True)
    b = fields.Integer(required=False, validate=lambda a: a > 11,missing=22)


class TestValidate(unittest.TestCase):
    def test_restful_validate(self):
        verifier = Test
        data = {
            "a": "c"
        }
        res = validate(verifier, data)
        self.assertEqual(len(res[1]), 0)
        self.assertEqual(res[0], data)

        res = validate(verifier, data, True)
        self.assertEqual(len(res[1]), 0)
        expected_res = {
            "a": "c",
            "b": 22
        }
        self.assertEqual(res[0], expected_res)

        data = {
            "a": 1,
            "b": 1
        }
        res = validate(verifier, data)
        self.assertEqual(len(res[1]), 2)


