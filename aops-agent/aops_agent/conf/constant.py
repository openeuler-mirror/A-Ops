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
import os

BASE_CONFIG_PATH = '/etc/aops'
BASE_SERVICE_PATH = '/usr/lib/systemd/system'

AGENT_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'aops_agent.conf')
DEFAULT_TOKEN_PATH = os.path.join(BASE_CONFIG_PATH, 'agent_token.json')
DATA_MODEL = {
    "str_array": {"type": "array", "items": {"type": "string", "minLength": 1}},
    "change_collect_items_request": {"type": "object",
                                     "additionalProperties":
                                         {"type": "object",
                                          "additionalProperties":
                                              {"enum": ["on", "off"]}}}}
INSTALLABLE_PLUGIN = ['gopher']
RPM_INFO = {"gopher": "gala-gopher"}
