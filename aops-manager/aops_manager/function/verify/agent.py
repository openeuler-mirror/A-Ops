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
from marshmallow import validate


class AgentPluginInfoSchema(Schema):
    """
    validators for parameter of /manage/agent/plugin/info
    """
    host_id = fields.String(required=True)


class AgentHostInfoSchema(AgentPluginInfoSchema):
    """
    validators for parameter of /manage/agent/host/info/query
    """
    pass


class GetHostSceneSchema(Schema):
    """
    validators for parameter of /manage/host/scene/get
    """
    host_id = fields.String(
        required=True, validate=lambda s: len(s) > 0)


class SetAgentPluginStatusSchema(Schema):
    """
    validators for parameter of /manage/agent/plugin/set
    """
    host_id = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    plugins = fields.Dict(required=True, keys=fields.String(validate=lambda s: len(s) > 0),
                          values=fields.Str(validate=validate.OneOf(["active", "inactive"])))


class SetAgentMetricStatusSchema(Schema):
    """
    validators for parameter of /manage/agent/metrics/set
    """
    host_id = fields.String(
        required=True, validate=lambda s: len(s) > 0)
    plugins = fields.Dict(required=True, keys=fields.String(validate=lambda s: len(s) > 0),
                          values=fields.Dict(keys=fields.String(validate=lambda s: len(s) > 0),
                                             values=fields.Str(validate=validate.OneOf(["on",
                                                                                        "off",
                                                                                        "auto"]))))
