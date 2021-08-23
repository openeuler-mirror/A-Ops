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

from aops_utils.conf import constant


class AddHostSchema(Schema):
    """
    validators for parameter of /manage/host/add_host
    """
    host_list = fields.List(fields.Dict(), required=True)
    key = fields.String(required=True, validate=lambda s: len(s) > 0)


class HostSchema(Schema):
    """
    validator for host info
    """
    host_name = fields.String(required=True, validate=lambda s: len(s) > 0)
    host_group_name = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    public_ip = fields.IP(required=True)
    ssh_port = fields.Integer(
        required=True,
        validate=lambda x: constant.MAX_PORT >= x >= constant.MIN_PORT)
    management = fields.Boolean(required=True)
    username = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    password = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    sudo_password = fields.String(
        required=True, validate=lambda s: len(s) > 0)


class DeleteHostSchema(Schema):
    """
    validators for parameter of /manage/host/delete_host
    """
    host_list = fields.List(fields.String(), required=True)


class GetHostSchema(Schema):
    """
    validators for parameter of /manage/host/get_host
    """
    host_group_list = fields.List(fields.String(), required=True)
    management = fields.Boolean(required=False)
    sort = fields.String(required=False, validate=validate.OneOf(
        ["host_name", "host_group_name"]))
    direction = fields.String(
        required=False, validate=validate.OneOf(["desc", "asc"]))
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 > s > 0)


class AddHostGroupSchema(Schema):
    """
    validators for parameter of /manage/host/add_host_group
    """
    host_group_name = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    description = fields.String(required=True)


class DeleteHostGroupSchema(Schema):
    """
    validators for parameter of /manage/host/delete_host_group
    """
    host_group_list = fields.List(fields.String(), required=True)


class GetHostGroupSchema(Schema):
    """
    validators for parameter of /manage/host/get_host_group
    """
    sort = fields.String(required=False, validate=validate.OneOf(
        ["host_count", "host_group_name"]))
    direction = fields.String(
        required=False, validate=validate.OneOf(["desc", "asc"]))
    page = fields.Integer(required=False, validate=lambda s: s > 0)
    per_page = fields.Integer(required=False, validate=lambda s: 50 > s > 0)


class GetHostInfoSchema(Schema):
    """
    validators for parameter of /manage/host/get_host_information
    """
    host_list = fields.List(fields.String(), required=True)
    basic = fields.Boolean(required=False)
