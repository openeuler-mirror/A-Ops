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
from flask import Response, jsonify

from aops_agent.conf.constant import (
    INFORMATION_ABOUT_RPM_SERVICE,
    INSTALLABLE_PLUGIN,
    DATA_MODEL,
    PLUGIN_WITH_CLASS
)
from aops_agent.conf.status import StatusCode, PARAM_ERROR, SERVER_ERROR, SUCCESS
from aops_agent.log.log import LOGGER
from aops_agent.manages.command_manage import Command
from aops_agent.manages import plugin_manage
from aops_agent.tools.util import validate_data, plugin_status_judge


@Command.validate_token
def start_plugin(plugin_name: str) -> Response:
    """
    make plugin run

    Args:
        plugin_name (str)

    return:
        Response:code, msg
    """
    if plugin_name not in INSTALLABLE_PLUGIN:
        return jsonify(StatusCode.make_response_body(PARAM_ERROR))
    if plugin_name in INFORMATION_ABOUT_RPM_SERVICE.keys():
        service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name).get('service_name')
        if service_name is not None:
            plugin = plugin_manage.Plugin(service_name)
            status_code = plugin.start_service()
            return jsonify(StatusCode.make_response_body(status_code))
    return jsonify(StatusCode.make_response_body(SERVER_ERROR))


@Command.validate_token
def stop_plugin(plugin_name: str) -> Response:
    """
    make plugin stop

    Args:
        plugin_name (str)

    Returns:
        Response: code, msg
    """
    if plugin_name not in INSTALLABLE_PLUGIN:
        return jsonify(StatusCode.make_response_body(PARAM_ERROR))
    if plugin_name in INFORMATION_ABOUT_RPM_SERVICE.keys():
        service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name).get('service_name')
        if service_name is not None:
            plugin = plugin_manage.Plugin(service_name)
            status_code = plugin.stop_service()
            return jsonify(StatusCode.make_response_body(status_code))
    return jsonify(StatusCode.make_response_body(SERVER_ERROR))


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
        return jsonify(StatusCode.make_response_body(PARAM_ERROR))
    res = {'resp': {}}
    plugin_name_list = list(collect_items_status.keys())
    unsupported_plugin_list = []
    for plugin_name in plugin_name_list:

        if plugin_name not in INSTALLABLE_PLUGIN:
            LOGGER.warning(f'{plugin_name} is not supported by agent')
            unsupported_plugin_list.append(plugin_name)
            continue

        if not plugin_status_judge(plugin_name):
            LOGGER.warning(f'{plugin_name} is not installed by agent')
            unsupported_plugin_list.append(plugin_name)
            continue

        plugin_class_name = PLUGIN_WITH_CLASS.get(plugin_name, '')
        if hasattr(plugin_manage, plugin_class_name):
            plugin = getattr(plugin_manage, plugin_class_name)
            if hasattr(plugin, 'change_items_status'):
                res['resp'][plugin_name] = plugin.change_items_status(
                    collect_items_status[plugin_name])
        else:
            LOGGER.warning(f'{plugin_name} is not supported by collect items')
            unsupported_plugin_list.append(plugin_name)

    for unsupported_plugin in unsupported_plugin_list:
        res['resp'][unsupported_plugin] = {
            'success': [],
            'failure': list(collect_items_status.get(unsupported_plugin).keys())
        }

    return jsonify(StatusCode.make_response_body((SUCCESS, res)))
