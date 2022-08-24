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
from marshmallow import Schema
from marshmallow import fields


class QueryCheckResultHostSchema(Schema):
    alert_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class QueryCheckResultListSchema(Schema):
    page = fields.Integer(validate=lambda x: x > 0)
    per_page = fields.Integer(validate=lambda x: 50 >= x > 0)
    domain = fields.String(validate=lambda x: len(x) > 0)
    level = fields.String(validate=lambda x: len(x) > 0)
    confirmed = fields.Boolean()
    sort = fields.String(validate=lambda x: x in ('time',))
    direction = fields.String(validate=lambda x: x in ('asc', 'desc'))
