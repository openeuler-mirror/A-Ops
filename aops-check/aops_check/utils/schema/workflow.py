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
from marshmallow import Schema, fields, validate


class CreateWorkflowHostInfoSchema(Schema):
    domain = fields.Integer(required=True, validate=lambda s: s > 0)
    hosts = fields.List(fields.String, required=True, validate=lambda s: len(s) > 0)


class CreateWorkflowSchema(Schema):
    workflow_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    description = fields.String(required=True, validate=lambda s: len(s) > 0)
    app_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    app_id = fields.String(required=True, validate=lambda s: len(s) > 0)
    input = fields.Nested(CreateWorkflowHostInfoSchema, required=True)
    step = fields.Integer(required=False)
    period = fields.Integer(required=False)
    alert = fields.Dict(required=False)


class QueryWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class QueryWorkflowListSchema(Schema):
    domain = fields.Integer(required=False, validate=lambda s: s > 0)
    status = fields.Integer(required=False, validate=validate.OneOf(
        ["hold", "running", "recommending"]))
    page = fields.Integer(required=False, validate= lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 0 < s < 50)


class DeleteWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class WorkflowDetailSchema(Schema):
    singlecheck = fields.Dict(required=False)
    multicheck = fields.Dict(required=False)
    diag = fields.String(required=False)


class UpdateWorkflowSchema(Schema):
    detail = fields.Nested(WorkflowDetailSchema, required=True)


class IfHostInWorkflowSchema(Schema):
    host_list = fields.List(fields.String, required=True, validate=lambda s: len(s) > 0)
