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
from marshmallow import Schema
from marshmallow import fields


class QueryAppSchema(Schema):
    app_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class QueryAppListSchema(Schema):
    page = fields.Integer(required=False, validate=lambda x: x > 0)
    per_page = fields.Integer(required=False, validate=lambda x: x > 0)


class ApiSchema(Schema):
    type = fields.String(required=True, validate=lambda s: len(s) > 0)
    address = fields.String(required=True, validate=lambda s: len(s) > 0)


class CreateAppSchema(Schema):
    app_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    version = fields.String(required=False)
    description = fields.String(required=True, validate=lambda s: len(s) > 0)
    api = fields.Nested(ApiSchema, required=True)
    detail = fields.Dict()
