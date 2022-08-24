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
Description: manager constant
"""
import os
from aops_utils.conf.constant import BASE_CONFIG_PATH

# path of manager configuration
MANAGER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'manager.ini')

TEMPLATE_INDEX = "ansible_templates"
TASK_INDEX = "ansible_task"
HOST_INFO_INDEX = 'host_information'

ROUTE_AGENT_PLUGIN_INFO = '/v1/agent/plugin/info'
ROUTE_AGENT_HOST_INFO = '/v1/agent/basic/info'

# agent
AGENT_PLUGIN_START = "/v1/agent/plugin/start"
AGENT_PLUGIN_STOP = "/v1/agent/plugin/stop"
AGENT_COLLECT_ITEMS_CHANGE = "/v1/agent/collect/items/change"
AGENT_APPLICATION_INFO = "/v1/agent/application/info"
ROUTE_AGENT_COLLECT_FILE = '/v1/agent/file/collect'

# check
CHECK_IDENTIFY_SCENE = "/check/scene/identify"
CHECK_WORKFLOW_HOST_EXIST = '/check/workflow/host/exist'