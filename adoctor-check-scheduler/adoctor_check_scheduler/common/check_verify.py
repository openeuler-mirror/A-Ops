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
Author: YangYunYi
Date: 2021/8/4 17:20
docs: check_verify.py
description: check verify params
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate


class DataItemSchema(Schema):
    """
    validator for data item info
    """
    name = fields.String(required=True, validate=lambda s: len(s) > 0)
    type = fields.String(required=False, validate=validate.OneOf(["log", "kpi"]))
    label = fields.Dict(required=False)


class CheckItemSchema(Schema):
    """
    validator for check item info
    """
    check_item = fields.String(required=True, validate=lambda s: len(s) > 0)
    data_list = fields.List(fields.Nested(DataItemSchema), required=True)
    condition = fields.String(required=True, validate=lambda s: len(s) > 0)
    description = fields.String(required=False)
    plugin = fields.String(required=True)


class ImportRuleSchema(Schema):
    """
    validators for parameter of /check/rule/import
    """
    check_items = fields.List(fields.Nested(CheckItemSchema), required=True)


class GetCheckRuleSchema(Schema):
    """
    validators for parameter of /check/rule/get
    """
    check_items = fields.List(fields.String(), required=True)
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 >= s > 0)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["check_item", ""]))
    direction = fields.String(required=False, validate=validate.OneOf(["desc", "asc"]))


class DeleteCheckRuleSchema(Schema):
    """
    validators for parameter of /check/rule/delete
    """
    check_items = fields.List(fields.String(), required=True, validate=lambda s: len(s) >= 0)


class GetCheckResultSchema(Schema):
    """
    validators for parameter of /check/result/get
    """
    time_range = fields.List(fields.Integer(),
                             validate=lambda s: len(s) == 2 or len(s) == 0, required=True)
    check_items = fields.List(fields.String(), required=True)
    host_list = fields.List(fields.String(), required=True)
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 >= s > 0)
    sort = fields.String(required=False, validate=validate.OneOf(["start",
                                                                  "end",
                                                                  "check_item",
                                                                  ""]))
    direction = fields.String(required=False, validate=validate.OneOf(["desc", "asc"]))
    value = fields.String(required=False)


class GetCheckResultCountSchema(Schema):
    """
    validators for parameter of /check/result/count
    """
    host_list = fields.List(fields.String(), required=True)
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 >= s > 0)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["count", ""]))
    direction = fields.String(required=False, validate=validate.OneOf(["desc", "asc"]))


class HostInfoSchema(Schema):
    """
    validators for parameter of host info in host list
    """
    host_id = fields.String(required=True, validate=lambda s: len(s) > 0)
    public_ip = fields.String(required=True, validate=lambda s: len(s) > 0)


class RetryTaskMsgSchema(Schema):
    """
    validators for parameter of retry task schema
    """
    time_range = fields.List(fields.Integer(), validate=lambda s: len(s) == 2, required=True)
    user = fields.String(required=True, validate=lambda s: len(s) > 0)
    host_list = fields.List(fields.Nested(HostInfoSchema),
                            required=True, validate=lambda s: len(s) > 0)
    check_items = fields.List(fields.String(), required=True)
    task_id = fields.Integer(required=True, validate=lambda s: s > -3)
