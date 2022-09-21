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
from typing import Any, Dict, Union, List
import json

import connexion
import requests
from flask import jsonify

from aops_agent.models.custom_exception import InputError
from aops_agent.conf.constant import DATA_MODEL, DEFAULT_TOKEN_PATH
from aops_agent.conf import configuration
from aops_agent.conf.status import (
    PARAM_ERROR,
    HTTP_CONNECT_ERROR,
    SUCCESS,
    StatusCode,
    TOKEN_ERROR
)
from aops_agent.log.log import LOGGER
from aops_agent.manages.token_manage import TokenManage as TOKEN
from aops_agent.tools.util import (
    get_shell_data,
    validate_data,
    get_uuid,
    get_host_ip,
    save_data_to_file
)


class Command:

    def get_host_info(self, info_type: List[str]) -> dict:
        """
        get basic info about machine

        Args:
            info_type(list): e.g [memory, os, cpu, disk]

        Returns:
            int: status code
            dict: e.g
                {
                    'resp':
                        {
                            'os': {
                                'os_version': os_version,
                                'bios_version': bios_version,
                                'kernel': kernel_version
                                },
                            "cpu": {
                                "architecture": string,
                                "core_count": string,
                                "model_name": string,
                                "vendor_id": string,
                                "l1d_cache": string,
                                "l1i_cache": string,
                                "l2_cache": string,
                                "l3_cache": string
                                },
                            'memory':{
                            "size": "xx GB",
                            "total": int,
                            "info": [
                                {
                                    "size": "xx GB",
                                    "type": "DDR4",
                                    "speed": "xxxx MT/s",
                                    "manufacturer": "string"
                                }
                                ...
                                ]
                            }
                            'disk':[
                                {
                                  "capacity": xx GB,
                                  "model": "string",
                                }
                            ]
                        }
                }
        """
        host_info = {"resp": {}}

        for info_name in info_type:
            func_name = getattr(self, f"_get_{info_name}_info")
            host_info["resp"][info_name] = func_name()

        return host_info

    @staticmethod
    def __get_system_info() -> str:
        """
            get system name and its version

        Returns:
            str: e.g openEuler 21.09
        """
        try:
            os_data = get_shell_data(['cat', '/etc/os-release'])
        except InputError:
            LOGGER.error('Get system info error,linux has no command!')
            return ''

        res = re.search('(?=PRETTY_NAME=).+', os_data)
        if res:
            return res.group()[12:].strip('"')
        LOGGER.warning('Get os version fail, please check file /etc/os-release and try it again')
        return ''

    def _get_os_info(self) -> Dict[str, str]:
        """
            get os info

        Returns:
                {
                    'os_version': string,
                    'bios_version': string,
                    'kernel': string
                }
        """
        res = {
            'os_version': self.__get_system_info(),
            'bios_version': self.__get_bios_version(),
            'kernel': self.__get_kernel_version()
        }
        return res

    @staticmethod
    def __get_bios_version() -> str:
        """
            get bios version number

        Returns:
            str
        """
        try:
            bios_data = get_shell_data(['dmidecode', '-t', 'bios'])
        except InputError:
            LOGGER.error('Get system info error,linux has no command dmidecode!')
            return ''

        res = re.search('(?=Version:).+', bios_data)

        if res:
            return res.group()[8:].strip()
        LOGGER.warning('Get bios version fail, please check dmidecode and try it again')
        return ''

    @staticmethod
    def __get_kernel_version() -> str:
        """
            get kernel version number

        Returns:
            str
        """
        try:
            kernel_data = get_shell_data(['uname', '-r'])
        except InputError:
            LOGGER.error('Get system info error,linux has no command!')
            return ''
        res = re.search(r'[\d\.]+-[\d\.]+[\d]', kernel_data)
        if res:
            return res.group()
        LOGGER.warning('Get kernel version fail, please check dmidecode and try it again')
        return ''

    @staticmethod
    def _get_cpu_info() -> Dict[str, str]:
        """
        get cpu info by command lscpu

        Returns:
            dict: e.g
                {
                    "architecture": string,
                    "core_count": string,
                    "model_name": string,
                    "vendor_id": string,
                    "l1d_cache": string,
                    "l1i_cache": string,
                    "l2_cache": string,
                    "l3_cache": string
                }
        """
        try:
            lscpu_data = get_shell_data(['lscpu'], env={"LANG": "en_US.utf-8"})
        except InputError:
            LOGGER.error('Get cpu info error,linux has no command lscpu or grep.')
            return {}

        info_list = re.findall('.+:.+', lscpu_data)
        if not info_list:
            LOGGER.warning('Failed to read cpu info by lscpu, please check it and try again.')

        cpu_info = {}
        for info in info_list:
            tmp = info.split(":")
            cpu_info[tmp[0]] = tmp[1].strip()

        res = {
            "architecture": cpu_info.get('Architecture'),
            "core_count": cpu_info.get('CPU(s)'),
            "model_name": cpu_info.get('Model name'),
            "vendor_id": cpu_info.get('Vendor ID'),
            "l1d_cache": cpu_info.get('L1d cache'),
            "l1i_cache": cpu_info.get('L1i cache'),
            "l2_cache": cpu_info.get('L2 cache'),
            "l3_cache": cpu_info.get('L3 cache')
        }

        return res

    @staticmethod
    def __get_total_online_memory() -> str:
        """
        get memory size by lsmem

        Returns:
            str: memory size
        """
        try:
            lsmem_data = get_shell_data(['lsmem'])
        except InputError:
            LOGGER.error('Get host memory info error, Linux has no command dmidecode')
            return ''

        res = re.search("(?=Total online memory:).+", lsmem_data)
        if res:
            return res.group()[20:].strip()
        LOGGER.warning('Get Total online memory fail, please check lsmem and try it again')
        return ''

    @staticmethod
    def _get_memory_info() -> Dict[str, Union[int, List[Dict[str, Any]]]]:
        """
        get memory detail info and memory stick count

        Returns:
            dict: e.g
                {
                    "size": "xx GB",
                    "total": int,
                    "info": [
                        {
                            "size": "xx GB",
                            "type": "DDR4",
                            "speed": "xxxx MT/s",
                            "manufacturer": "string"
                        }
                        ...
                        ]
                }

        """
        res = {}
        if Command.__get_total_online_memory():
            res['size'] = Command.__get_total_online_memory()

        try:
            memory_data = get_shell_data(['dmidecode', '-t', 'memory']).split('Memory Device')
        except InputError:
            LOGGER.error('Get host memory info error, Linux has no command dmidecode')
            return res

        if len(memory_data) == 1:
            LOGGER.warning('Failed to read memory info by dmidecode')
            return res

        info = []
        for module in memory_data:
            module_info_list = re.findall('.+:.+', module)

            module_info_dict = {}
            for module_info in module_info_list:
                part_info = module_info.split(':')
                module_info_dict[part_info[0].strip()] = part_info[1].strip()

            if module_info_dict.get('Size') is None or \
                    module_info_dict.get('Size') == 'No Module Installed':
                continue

            memory_info = {
                "size": module_info_dict.get('Size'),
                "type": module_info_dict.get('Type'),
                "speed": module_info_dict.get('Speed'),
                "manufacturer": module_info_dict.get('Manufacturer')
            }
            info.append(memory_info)

        res['total'] = len(info)
        res['info'] = info

        return res

    @classmethod
    def validate_token(cls, func) -> Any:
        """
        validate if the token is correct

        Returns:
            return func when token is correct,
            return error info when token is incorrect.
        """

        def wrapper(*arg, **kwargs):
            token = TOKEN.get_value()
            access_token = connexion.request.headers.get('access_token')
            if token == '' or access_token != token:
                LOGGER.warning("token is incorrect when request %s" % connexion.request.path)
                return jsonify(StatusCode.make_response_body(TOKEN_ERROR))
            return func(*arg, **kwargs)

        return wrapper

    @classmethod
    def register(cls, register_info: dict) -> int:
        """
        register on manager
        Args:
            register_info(dict): It contains the necessary information to register an account
            for example:
            {
              "web_username": "string",
              "web_password": "string",
              "manager_ip": "string",
              "manager_port": "string",
              "host_name": "string",
              "host_group_name": "string",
              "management": true
            }
        Returns:
            str: status code
        """
        if not validate_data(register_info, DATA_MODEL.get('register_schema')):
            return PARAM_ERROR

        data = {}
        data['host_name'] = register_info.get('host_name')
        data['host_group_name'] = register_info.get('host_group_name')
        data['management'] = register_info.get('management') or False
        data['username'] = register_info.get('web_username')
        data['password'] = register_info.get('web_password')
        data['host_id'] = get_uuid()
        data['public_ip'] = get_host_ip()
        data['agent_port'] = register_info.get('agent_port') or \
                             configuration.agent.get('PORT')

        manager_ip = register_info.get('manager_ip')
        manager_port = register_info.get('manager_port')
        url = f'http://{manager_ip}:{manager_port}/manage/host/add'
        try:
            ret = requests.post(url, data=json.dumps(data),
                                headers={'content-type': 'application/json'}, timeout=5)
        except requests.exceptions.ConnectionError as e:
            LOGGER.error(e)
            return HTTP_CONNECT_ERROR
        ret_data = json.loads(ret.text)
        if ret_data.get('code') == SUCCESS:
            TOKEN.set_value(ret_data.get('token'))
            save_data_to_file(json.dumps({"access_token": ret_data.get('token')}),
                              DEFAULT_TOKEN_PATH)
            return SUCCESS
        LOGGER.error(ret_data)
        return int(ret_data.get('code'))

    @staticmethod
    def _get_disk_info() -> List[Dict]:
        """
            get disk capacity and model

        Returns:
            list: e.g
                [
                    {
                      "capacity": string,
                      "model": "string",
                    }
                ]
        """
        try:
            lshw_data = get_shell_data(['lshw', '-json', '-c', 'disk'])
        except InputError:
            LOGGER.error('Failed to get hard disk info, Linux has no command lshw')
            return []

        # Convert the command result to a json string
        # lshw_data e.g  "{...},{...},{...}"
        lshw_data = f"[{lshw_data}]"

        try:
            disk_info_list = json.loads(lshw_data)
        except json.decoder.JSONDecodeError:
            LOGGER.warning("unexpected execution result, "
                           "please check command 'lshw -json -c disk'")
            disk_info_list = []

        res = []
        if disk_info_list:
            for disk_info in disk_info_list:
                tmp = {
                    "model": disk_info.get('product'),
                    "capacity": f"{disk_info.get('size', 0) // 10 ** 9}GB"
                }
                res.append(tmp)

        return res
