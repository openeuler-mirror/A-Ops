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
from typing import List, Dict
import libconf
from aops_agent.conf import configuration
from aops_agent.conf.constant import INSTALLABLE_PLUGIN
from aops_agent.conf.status import (
    SUCCESS,
    FILE_NOT_FOUND,
    CONFLICT_ERROR
)
from aops_agent.tools.util import (
    get_shell_data,
    load_gopher_config,
    plugin_status_judge,
    change_probe_status
)


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

    def start_service(self) -> int:
        """
        make plugin running

        Returns:
            int: status code
        """
        status_info = get_shell_data(["systemctl", "status", f"{self.rpm_name}"], key=False)
        plugin_status = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
        if "running" in plugin_status:
            return SUCCESS
        res = get_shell_data(["systemctl", "start", f"{self.rpm_name}"])
        if res == "":
            return SUCCESS
        if "service not found" in res:
            return FILE_NOT_FOUND
        return CONFLICT_ERROR

    def stop_service(self) -> int:
        """
        make plugin stopping

        Returns:
            int: status code
        """
        status_info = get_shell_data(["systemctl", "status", f"{self.rpm_name}"], key=False)
        plugin_status = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
        if "inactive" in plugin_status:
            return SUCCESS
        res = get_shell_data(["systemctl", "stop", f"{self.rpm_name}"])
        if res == "":
            return SUCCESS
        return FILE_NOT_FOUND

    @classmethod
    def get_installed_plugin(cls) -> List[str]:
        """
        get plugin list is which installed

        Returns:
            List[str]: list about rpm package name
            For example:
                [app1, app2, app3]
        """
        installed_plugin = INSTALLABLE_PLUGIN.copy()
        if len(installed_plugin) == 0:
            return []

        for plugin_name in INSTALLABLE_PLUGIN:
            if not plugin_status_judge(plugin_name):
                installed_plugin.remove(plugin_name)
        return installed_plugin

    def get_plugin_status(self):
        """
        Get plugin running status which is installed

        Returns:
            str: dead or running

        """
        plugin_status = get_shell_data(["systemctl", "status", f"{self.rpm_name}"], key=False)
        active_string = get_shell_data(["grep", "Active"], stdin=plugin_status.stdout)
        status = re.search(':.+\(', active_string).group()[1:-1].strip()
        return status

    @classmethod
    def get_pid(cls, rpm_name):
        """
        Get main process id when plugin is running

        Returns:
            The str type of main process id
        """
        res = get_shell_data(["systemctl", "status", f"{rpm_name}"], key=False)
        main_pid_info = get_shell_data(["grep", "Main"], stdin=res.stdout)
        main_pid = re.search("[0-9]+[0-9]", main_pid_info).group()
        return main_pid


class GalaGopher(Plugin):
    """
    Some methods only available to Gopher
    """
    _rpm = 'gala-gopher'
    _name = 'gala-gopher'

    @classmethod
    def get_collect_items(cls) -> set:
        """
        Get gopher probes name and extend_probes name

        Returns:
            A set which includes probe's name and extend_probe's name
        """
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            return set()
        probes = set()
        for probe_list in (cfg.get("probes", ()), cfg.get("extend_probes", ())):
            for probe in probe_list:
                probe_name = probe.get("name", "")
                if probe_name:
                    probes.add(probe_name)
        return probes

    @classmethod
    def change_items_status(cls, gopher_probes_status: Dict[str, str]) \
            -> Dict[str, List[str]]:
        """
        Change running status about probe

        Args:
            A dict type data about some probe's status
            for example:

            gopher_probes_status:   {probe1: xx,
                                    probe2: xx,
                                    probe3: xx}

        Returns:
            Dict[str, List[str]]
            for example:
                {
                'success': ['probe1','probe2','probe3'].
                'failure': ['probe1','probe2','probe3'].
                }

        Raises:
            PermissionError: create file failure
        """
        res = {'success': []}
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            res['failure'] = list(gopher_probes_status.keys())
            return res
        probes = cfg.get("probes", ())
        extend_probes = cfg.get('extend_probes', ())
        res, failure = change_probe_status(probes, gopher_probes_status, res)
        res, failure = change_probe_status(extend_probes, failure, res)
        res['failure'] = list(failure.keys())
        gopher_config_path = configuration.gopher.get('CONFIG_PATH')
        with open(gopher_config_path, 'w', encoding='utf8') as cf:
            cf.write(libconf.dumps(cfg))
        return res

    @classmethod
    def get_collect_status(cls) -> List[dict]:
        """
        get probe status

        Returns:
            dict which contains status code,data or error info
        """
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            return []
        porbe_list = []
        for probes in (cfg.get('probes', ()), cfg.get('extend_probes', ())):
            for probe in probes:
                probe_info = {'support_auto': False}
                if 'start_check' in probe:
                    probe_info['support_auto'] = True
                if 'name' in probe and 'switch' in probe:
                    probe_info['probe_name'] = probe['name']
                    probe_info['probe_status'] = probe['switch']
                    porbe_list.append(probe_info)
        return porbe_list
