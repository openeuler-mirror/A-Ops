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
from typing import List

from aops_agent.conf.constant import INSTALLABLE_PLUGIN, RPM_INFO
from aops_agent.manages import plugin_manage
from aops_agent.manages.command_manage import Command
from aops_agent.manages.resource_manage import Resourse
from aops_agent.tools.util import plugin_install_judge


@Command.validate_token
def get_host_info() -> dict:
    """
    get basic info about machine

    Returns:
        a dict which contains os info,bios version and kernel version
    """
    return Command.get_host_info()


@Command.validate_token
def agent_plugin_info() -> List[dict]:
    """
    get all info about agent

    Returns:
        a list which contains cpu,memory,collect items of plugin,running status and so on.for
        example
    [{
    "plugin_name": "string",
    "is_installed": true,
    "status": "string",
    "collect_items": [{
                    "probe_name": "string",
                    "probe_status": "string"} ],
    "resource": [{
                "name": "string",
                "limit_value": "string",
                "current_value": "string}]}]
    """
    plugin_list = INSTALLABLE_PLUGIN
    if len(plugin_list) == 0:
        return []

    res = []
    for plugin_name in plugin_list:
        plugin_running_info = {'plugin_name': plugin_name}

        if not plugin_install_judge(plugin_name):
            plugin_running_info['is_installed'] = False
            continue
        else:
            plugin_running_info['is_installed'] = True

        rpm_name = RPM_INFO.get(plugin_name)
        plugin = plugin_manage.Plugin(rpm_name)
        status = plugin.get_plugin_status()

        if status == 'active':
            pid = plugin_manage.Plugin.get_pid(rpm_name)
            cpu_current = Resourse.get_cpu(rpm_name, pid)
            memory_current = Resourse.get_memory(pid)
        else:
            cpu_current = None
            memory_current = None

        cpu_limit = Resourse.get_cpu_limit(rpm_name)
        memory_limit = Resourse.get_memory_limit(rpm_name)

        collect_items_status = []
        if hasattr(plugin_manage, plugin_name.title()):
            plugin_obj = getattr(plugin_manage, plugin_name.title())
            if hasattr(plugin_obj, 'get_collect_items'):
                collect_items_status = plugin_obj.get_collect_status()

        resource = []
        cpu = {}
        cpu['name'] = 'cpu'
        cpu['current_value'] = cpu_current
        cpu['limit_value'] = cpu_limit
        memory = {}
        memory['name'] = 'memory'
        memory['current_value'] = memory_current
        memory['limit_value'] = memory_limit
        resource.append(cpu)
        resource.append(memory)
        plugin_running_info['status'] = status
        plugin_running_info['collect_items'] = collect_items_status
        plugin_running_info['resource'] = resource
        res.append(plugin_running_info)
    return res
