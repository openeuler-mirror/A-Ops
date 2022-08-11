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
                                              {"enum": ["on", "off", "auto"]}}},
    'register_schema': {
        "type": "object",
        "required": ["host_name",
                     "host_group_name",
                     "web_username",
                     "web_password",
                     "management",
                     "manager_ip",
                     "manager_port"],
        "properties": {
            "host_name": {"type": "string", "minLength": 1},
            "host_group_name": {"type": "string", "minLength": 1},
            "web_username": {"type": "string", "minLength": 1},
            "web_password": {"type": "string", "minLength": 1},
            "management": {"enum": [True, False]},
            "manager_ip": {"type": "string", "minLength": 8},
            "manager_port": {"type": "string", "minLength": 2},
            "agent_port": {"type": "string", "minLength": 1}
        }}}
INSTALLABLE_PLUGIN = ['gopher']
INFORMATION_ABOUT_RPM_SERVICE = {
    "gopher":   {"rpm_name": "gala-gopher", "service_name": "gala-gopher"},
    "mysql":    {"rpm_name": "mysql5",      "service_name": "mysqld"},
    "k8s":      {"rpm_name": "kubernetes",  "service_name": "kubernetes"},
    "hadoop":   {"rpm_name": "hadoop",      "service_name": "hadoop"},
    "nginx":    {"rpm_name": "nginx",       "service_name": "nginx"},
    "docker":   {"rpm_name": "docker",      "service_name": "docker"},
}
SCANNED_APPLICATION = ["mysql", "k8s", "hadoop", "nginx", "docker", "gopher"]
REGISTER_HELP_INFO = """
    you can choose start or register in manager,
    if you choose register,you need to provide the following information.
    you can input it by '-d' 'json-string' or 
            input it from file by '-f' '/xxxx/.../xx.json'
    
    Required parameter: All information cannot be empty
    host_name               type: string
    host_group_name         type: string
    web_username            type: string
    web_password            type: string
    management              type: boolean,only True or False
    manager_ip              type: string
    manager_port            type: string
    
    optional parameter: 
    agent_port              type: string
    
    for example:
    {
    "web_username":"xxx",
    "web_password": "xxx",
    "host_name": "xxx",
    "host_group_name": "xxx", 
    "manager_ip":"192.168.xx.xx",
    "management":false,
    "manager_port":"11111",
    "agent_port":"12000"
    }

"""
