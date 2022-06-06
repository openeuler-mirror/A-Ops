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
Description: For repo related restful interfaces schema
"""
from marshmallow import Schema
from marshmallow import fields


class ImportYumRepoSchema(Schema):
    """
    validators for parameter of /vulnerability/repo/import
    """
    repo_name = fields.String(
        required=True, validate=lambda s: 0 < len(s) < 20)
    repo_data = fields.String(
        required=True, validate=lambda s: 0 < len(s) < 512)


class GetYumRepoSchema(Schema):
    """
    validators for parameter of /vulnerability/repo/get. when empty, get all repos
    """
    repo_name_list = fields.List(fields.String(), required=True)


class UpdateYumRepoSchema(Schema):
    """
    validators for parameter of /vulnerability/repo/update
    """
    repo_name = fields.String(
        required=True, validate=lambda s: 0 < len(s) < 20)
    repo_data = fields.String(
        required=True, validate=lambda s: 0 < len(s) < 512)


class DeleteYumRepoSchema(Schema):
    """
    validators for parameter of /vulnerability/repo/delete
    """
    repo_name_list = fields.List(fields.String(), required=True)
