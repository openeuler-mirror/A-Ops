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
    domain = fields.String(required=True, validate=lambda s: len(s) > 0)
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


class WorkflowListFilterSchema(Schema):
    """
    filter schema of workflow list getting interface
    """
    domain = fields.List(fields.String, required=False, validate=lambda s: len(s) > 0)
    app = fields.List(fields.String, required=False, validate=lambda s: len(s) > 0)
    status = fields.List(fields.String(validate=validate.OneOf(["hold", "running", "recommending"])),
                         required=False)


class QueryWorkflowListSchema(Schema):
    filter = fields.Nested(WorkflowListFilterSchema, required=False)
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 0 < s < 50)


class ExecuteWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class StopWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class DeleteWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)


class WorkflowDetailSchema(Schema):
    singlecheck = fields.Dict(required=False)
    multicheck = fields.Dict(required=False)
    diag = fields.String(required=False)


class UpdateWorkflowSchema(Schema):
    workflow_id = fields.String(required=True, validate=lambda s: len(s) > 0)
    workflow_name = fields.String(required=False, validate=lambda s: len(s) > 0)
    description = fields.String(required=False, validate=lambda s: len(s) > 0)
    step = fields.Integer(required=False)
    period = fields.Integer(required=False)
    alert = fields.Dict(required=False)
    detail = fields.Nested(WorkflowDetailSchema, required=False)


class IfHostInWorkflowSchema(Schema):
    host_list = fields.List(fields.String, required=True, validate=lambda s: len(s) > 0)
