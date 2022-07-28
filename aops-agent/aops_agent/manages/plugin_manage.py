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
import re
from dataclasses import dataclass
from typing import List

from flask import Response

from aops_agent.conf.constant import INSTALLABLE_PLUGIN, RPM_INFO
from aops_agent.tools.util import get_shell_data, create_response


@dataclass
class Plugin:
    """
    Provide some functions to control plugin,
    such as  start, stop, get running info and so on.

    Attributes:
        _rpm_name: the rpm package name
    """
    __slots__ = "_rpm_name"
    _rpm_name: str

    @property
    def rpm_name(self) -> str:
        return self._rpm_name

    def start_service(self) -> Response:
        """
        make plugin running

        Returns:
            Response: main pid about plugin or failure info

        """
        res = get_shell_data(["systemctl", "start", f"{self.rpm_name}"])
        if res == "":
            status_info = get_shell_data(["systemctl", "status", f"{self.rpm_name}"], key=False)
            main_pid_info = get_shell_data(["grep", "Main"], stdin=status_info.stdout)
            main_pid = re.search("[0-9]+[0-9]", main_pid_info).group()
            return create_response(200, main_pid)
        if "service not found" in res:
            msg = "plugin is not installed"
            return create_response(410, msg)
        return create_response(409, res)

    def stop_service(self) -> Response:
        """
        make plugin stopping

        Returns:
            Response: success info or failure info
        """
        status_info = get_shell_data(["systemctl", "status", f"{self.rpm_name}"], key=False)
        plugin_status = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
        if "inactive" in plugin_status:
            msg = f"{self.rpm_name} has stopped !"
            return create_response(202, msg)

        res = get_shell_data(["systemctl", "stop", f"{self.rpm_name}"])
        if res == "":
            return create_response(200, f"{self.rpm_name} stop success !")
        msg = "plugin is not installed"
        return create_response(410, msg)

    @classmethod
    def get_plugin_installed(cls) -> List[str]:
        """
        get plugin list is which installed

        Returns:
            List[str]: list about rpm package name
            For example:
                [app1, app2, app3]
        """
        installable_plugin_list = INSTALLABLE_PLUGIN
        if len(installable_plugin_list) == 0:
            return []

        for plugin_name in INSTALLABLE_PLUGIN:
            rpm_name = RPM_INFO.get(plugin_name, "")
            status_info = get_shell_data(["systemctl", "status", rpm_name], key=False)
            plugin_status = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
            if plugin_status == "":
                installable_plugin_list.remove(plugin_name)
        return installable_plugin_list
