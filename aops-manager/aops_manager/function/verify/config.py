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


class ConfigSchema(Schema):
    """
        validators for CollectConfigSchema
    """
    host_id = fields.String(required=True, validate=lambda s: len(s) > 0)
    config_list = fields.List(fields.String(required=True, validate=lambda s: len(s) > 0),
                              required=True,
                              validate=lambda s: len(s) > 0)


class CollectConfigSchema(Schema):
    """
    validators for parameter of /manage/config/collect
    """
    infos = fields.List(fields.Nested(ConfigSchema(), required=True), required=True, validate=lambda s: len(s) > 0)
