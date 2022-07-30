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
import json

from flask import Response

from aops_agent.conf.constant import RPM_INFO, INSTALLABLE_PLUGIN, DATA_MODEL
from aops_agent.conf.status import StatusCode, SUCCESS, PARAM_ERROR
from aops_agent.manages.command_manage import Command
from aops_agent.manages import plugin_manage
from aops_agent.tools.util import create_response, validate_data, plugin_install_judge


@Command.validate_token
def start_plugin(plugin_name: str) -> Response:
    """
    make plugin run

    Args:
        plugin_name (str)

    return:
        Response: main pid of process or failure info
    """
    if plugin_name not in INSTALLABLE_PLUGIN:
        msg = json.dumps(StatusCode.make_response_body(PARAM_ERROR))
        return create_response(PARAM_ERROR, msg)
    plugin = plugin_manage.Plugin(RPM_INFO.get(plugin_name, ""))
    res = plugin.start_service()
    return create_response(res[0], res[1])


@Command.validate_token
def stop_plugin(plugin_name: str) -> Response:
    """
    make plugin stop

    Args:
        plugin_name (str)

    Returns:
        Response: success or failure info
    """
    if plugin_name not in INSTALLABLE_PLUGIN:
        msg = json.dumps(StatusCode.make_response_body(PARAM_ERROR))
        return create_response(PARAM_ERROR, msg)
    plugin = plugin_manage.Plugin(RPM_INFO.get(plugin_name, ""))
    res = plugin.start_service()
    return create_response(res[0], res[1])


@Command.validate_token
def change_collect_items(collect_items_status) -> Response:
    """
    change collect items about plugin

    Args:
        collect_items_status(dict): A dict which contains collect items and its status

    Returns:
        Response which contains update result or error info
    """
    if validate_data(collect_items_status,
                     DATA_MODEL.get("change_collect_items_request")) is False:
        return create_response(PARAM_ERROR,
                               json.dumps(StatusCode.make_response_body(PARAM_ERROR)))
    res = {}
    plugin_name_list = list(collect_items_status.keys())
    for plugin_name in plugin_name_list:

        if plugin_name not in INSTALLABLE_PLUGIN:
            res[plugin_name] = 'It\'s not support by agent'
            continue

        if not plugin_install_judge(plugin_name):
            res[plugin_name] = 'It\'s not installed by agent'
            continue

        if hasattr(plugin_manage, plugin_name.title()):
            plugin = getattr(plugin_manage, plugin_name.title())
            if hasattr(plugin, 'change_items_status'):
                res[plugin_name] = plugin.change_items_status(collect_items_status[plugin_name])
        else:
            res[plugin_name] = 'It\'s not  support by collect items'
    return create_response(SUCCESS, json.dumps(res))
