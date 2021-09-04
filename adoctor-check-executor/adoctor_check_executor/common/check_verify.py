#!/usr/bin/env python3
# -*- coding:UTF=8 -*-
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/30 17:26
docs: check_verify.py
description: check verify schema
"""

from marshmallow import Schema
from marshmallow import fields


class HostInfoSchema(Schema):
    """
    validators for parameter of host info in host list
    """
    host_id = fields.String(required=True, validate=lambda s: len(s) > 0)
    public_ip = fields.String(required=True, validate=lambda s: len(s) > 0)


class CheckTaskMsgSchema(Schema):
    """
    validators for parameter of check task schema
    """
    time_range = fields.List(fields.Integer(),
                             validate=lambda s: len(s) == 2, required=True)
    user = fields.String(required=True, validate=lambda s: len(s) > 0)
    host_list = fields.List(fields.Nested(HostInfoSchema),
                            required=True, validate=lambda s: len(s) > 0)
    check_items = fields.List(fields.String(), required=True)
    task_id = fields.Integer(required=True, validate=lambda s: s > -3)
