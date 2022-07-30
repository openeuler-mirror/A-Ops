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
import configparser
import os
from dataclasses import dataclass

from aops_agent.conf.constant import BASE_SERVICE_PATH
from aops_agent.tools.util import load_conf, get_shell_data


@dataclass
class Resourse:
    """
    Get cpu and memory info
    """

    @classmethod
    def get_memory(cls, pid: str) -> str:
        """
        Get memory value which plugin has used
        Args:
            pid(str): main process id about running plugin
        Returns:
            str:The memory value which has used
        """
        memory_info = get_shell_data(["cat", f"/proc/{pid}/status"], key=False)
        memory = get_shell_data(["grep", "VmRSS"],
                                stdin=memory_info.stdout).split(":")[1].strip()
        return memory

    @classmethod
    def get_memory_limit(cls, rpm_name: str) -> str:
        """
        Get MemoryHigh value from service file

        Args:
            rpm_name (str): rpm package name

        Returns:
            str: memory_high values.

        Raises:
            NoOptionError: The service section has no option "MemoryHigh"
            NoSectionError: Service file has no section "Service"
        """
        service_path = os.path.join(BASE_SERVICE_PATH, f"{rpm_name}.service")
        config = load_conf(service_path)
        try:
            memory_high = config.get("Service", "MemoryHigh")
        except configparser.NoOptionError:
            memory_high = None
        except configparser.NoSectionError:
            memory_high = None
        return memory_high

    @classmethod
    def get_cpu(cls, rpm_name: str, pid: str) -> str:
        """
        Get cpu usage by process id

        Args:
            rpm_name(str): rpm package name
            pid(str): main process id about running plugin

        Returns:
            str: cpu usage
        """
        all_status_info = get_shell_data(["ps", "aux"], key=False)
        plugin_process_info = get_shell_data(["grep", "-w", f"{rpm_name}"],
                                             stdin=all_status_info.stdout, key=False)
        plugin_main_pid_process_info = get_shell_data(["grep", f"{pid}"],
                                                      stdin=plugin_process_info.stdout, key=False)
        cpu_usage = get_shell_data(["awk", "{print $3}"], stdin=plugin_main_pid_process_info.stdout)
        return f'{cpu_usage.strip()}%'

    @classmethod
    def get_cpu_limit(cls, rpm_name: str) -> str:
        """
        get limit cpu from plugin service file

        Args:
            rpm_name (str): rpm package name

        Returns:
            str: cpu limit value

        Raises:
            NoOptionError: The service section has no option "CPUQuota"
            NoSectionError: Service file has no section "Service"
        """
        service_path = os.path.join(BASE_SERVICE_PATH, f"{rpm_name}.service")
        config = load_conf(service_path)
        try:
            cpu_limit = config.get("Service", "CPUQuota")
        except configparser.NoOptionError:
            cpu_limit = None
        except configparser.NoSectionError:
            cpu_limit = None
        return cpu_limit
