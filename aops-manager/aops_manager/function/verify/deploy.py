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
Description: For host related interfaces
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate


class GenerateTaskSchema(Schema):
    """
    validators for parameter of /manage/task/generate_task
    """
    task_name = fields.String(required=True)
    description = fields.String(required=True)
    template_name = fields.List(fields.String(), required=True)


class ExecuteTaskSchema(Schema):
    """
    validators for parameter of /manage/task/execute_task
    """
    task_list = fields.List(fields.String(), required=True)


class GetTaskSchema(Schema):
    """
    validators for parameter of /manage/task/get_task
    """
    task_list = fields.List(fields.String(), required=True)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["task_name"]))
    direction = fields.String(
        required=False, validate=validate.OneOf(["desc", "asc"]))
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 > s > 0)


class DeleteTaskSchema(Schema):
    """
    validators for parameter of /manage/task/generate_task
    """
    task_list = fields.List(fields.String(), required=True)


class ImportTemplateSchema(Schema):
    """
    validators for parameter of /manage/template/import_template
    """
    template_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    template_content = fields.Dict(required=True)
    description = fields.String(required=True)


class DeleteTemplateSchema(Schema):
    """
    validators for parameter of /manage/template/delete_template
    """
    template_list = fields.List(fields.String(), required=True)


class GetTemplateSchema(Schema):
    """
    validators for parameter of /manage/template/get_template
    """
    template_list = fields.List(fields.String(), required=True)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["template_name"]))
    direction = fields.String(
        required=False, validate=validate.OneOf(["desc", "asc"]))
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 > s > 0)
