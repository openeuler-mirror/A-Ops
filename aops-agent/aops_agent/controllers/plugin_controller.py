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
from typing import Union

from flask import make_response, Response

from aops_agent.conf.constant import RPM_INFO, INSTALLABLE_PLUGIN
from aops_agent.manages.command_manage import Command
from aops_agent.manages.plugin_manage import Plugin
from aops_agent.tools.util import create_response


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
        msg = "plugin is not supported"
        return create_response(400, msg)
    rpm_name = RPM_INFO.get(plugin_name, "")
    plugin = Plugin(rpm_name)
    return plugin.start_service()



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
        msg = "plugin is not supported"
        return create_response(400, msg)
    rpm_name = RPM_INFO.get(plugin_name, "")
    plugin = Plugin(rpm_name)
    return plugin.stop_service()
