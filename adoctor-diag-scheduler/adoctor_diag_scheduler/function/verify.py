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
Description: For diagnose restful interfaces
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate


class DiagTreeInfoSchema(Schema):
    """
    single tree's info of /diag/tree/import
    """
    tree_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    tree_content = fields.Dict(required=True, validate=lambda s: s != {})
    description = fields.String(required=True)


class AddTreeSchema(Schema):
    """
    validators for parameter of /diag/tree/import
    """
    trees = fields.List(fields.Nested(DiagTreeInfoSchema), required=True,
                        validate=lambda s: len(s) > 0)


class GetTreeSchema(Schema):
    """
    validators for parameter of /diag/tree/get
    """
    # if null then query all trees
    tree_list = fields.List(fields.String(), required=True)


class DeleteTreeSchema(Schema):
    """
    validators for parameter of /diag/tree/delete
    """
    # if null, do nothing
    tree_list = fields.List(fields.String(), required=True)


class ExecuteDiagSchema(Schema):
    """
    validators for parameter of /diag/execute
    """
    host_list = fields.List(fields.String(), required=True, validate=lambda s: len(s) > 0)
    time_range = fields.List(fields.Integer(), validate=lambda s: len(s) == 2, required=True)
    tree_list = fields.List(fields.String(), required=True, validate=lambda s: len(s) > 0)
    interval = fields.Integer(required=True, validate=lambda s: s > 0)


class GetTaskSchema(Schema):
    """
    validators for parameter of /data/diag/task/get
    """
    sort = fields.String(required=False, validate=validate.OneOf(
        ["expected_report_num", "cur_report_num", "time"]))
    direction = fields.String(required=False, validate=validate.OneOf(
        ["asc", "desc"]))
    page = fields.Integer(required=False)
    per_page = fields.Integer(required=False)
    time_range = fields.List(fields.Integer, required=False, validate=lambda s: len(s) == 2)


class GetProgressSchema(Schema):
    """
    validators for parameter of /diag/progress/get
    """
    task_list = fields.List(fields.String(), required=True, validate=lambda s: len(s) > 0)


class GetReportSchema(Schema):
    """
    validators for parameter of /diag/report/get
    """
    report_list = fields.List(fields.String(), required=True, validate=lambda s: len(s) > 0)


class DeleteReportSchema(Schema):
    """
    validators for parameter of /diag/report/delete
    """
    # if null, do nothing
    report_list = fields.List(fields.String(), required=True)


class GetReportListSchema(Schema):
    """
    validators for parameter of /diag/report/get_list
    """
    time_range = fields.List(fields.Integer(), validate=lambda s: len(s) == 2, required=False)
    # if null, query all hosts
    host_list = fields.List(fields.String(), required=False)
    # if null, query all trees
    tree_list = fields.List(fields.String(), required=False)
    task_id = fields.String(required=False, validate=lambda s: len(s) > 0)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["time", "tree_name"]))
    direction = fields.String(
        required=False, validate=validate.OneOf(["desc", "asc"]))
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 >= s > 0)
