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
from typing import Any, Tuple
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
    TOKEN_ERROR,
    SERVER_ERROR
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

    @classmethod
    def get_host_info(cls) -> Tuple[int, dict]:
        """
        get basic info about machine

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
                                }
                        }
                }
        """
        try:
            os_data = get_shell_data(['cat', '/etc/os-release'], key=False)
            os_version_info = get_shell_data(['grep', 'PRETTY_NAME'], stdin=os_data.stdout)
            os_data.stdout.close()

            bios_data = get_shell_data(['dmidecode', '-t', '-0'], key=False)
            bios_version_info = get_shell_data(['grep', 'Version'], stdin=bios_data.stdout)
            bios_data.stdout.close()

            kernel_data = get_shell_data(['uname', '-r'])

            lscpu_data = get_shell_data(['lscpu'], key=False, env={"LANG": "en_US.utf-8"})
            cpu_data = get_shell_data(['grep',
                                       'Architecture\|CPU(s)\|Model name\|Vendor ID\|L1d cache\|L1i cache\|L2 cache\|L3 cache'],
                                      stdin=lscpu_data.stdout)
            lscpu_data.stdout.close()

        except InputError:
            LOGGER.error('Get host info error,linux has no command!')
            return SERVER_ERROR, {}

        os_version = os_version_info.split("=")[1].replace('\n', '').replace('"', '')
        bios_version = bios_version_info.split(':')[1].replace('\n', '').replace(' ', '')
        kernel_version = kernel_data[:re.search('[a-zA-Z]+', kernel_data).span()[0] - 1]

        cpu_info = {}
        for line in cpu_data.split('\n')[:-1]:
            tmp = line.split(":")
            if len(tmp) != 2:
                continue
            cpu_info[tmp[0]] = tmp[1].strip()

        host_info = {
            'resp': {
                'os': {
                    'os_version': os_version,
                    'bios_version': bios_version,
                    'kernel': kernel_version
                },
                'cpu': {
                    "architecture": cpu_info.get('Architecture'),
                    "core_count": cpu_info.get('CPU(s)'),
                    "model_name": cpu_info.get('Model name'),
                    "vendor_id": cpu_info.get('Vendor ID'),
                    "l1d_cache": cpu_info.get('L1d cache'),
                    "l1i_cache": cpu_info.get('L1i cache'),
                    "l2_cache": cpu_info.get('L2 cache'),
                    "l3_cache": cpu_info.get('L3 cache')
                }
            }
        }
        return SUCCESS, host_info

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
        else:
            LOGGER.error(ret_data)
            return int(ret_data.get('code'))
