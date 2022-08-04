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
from typing import Any
import json

import connexion
import requests
from flask import make_response

from aops_agent.conf.constant import DATA_MODEL
from aops_agent.conf import configuration
from aops_agent.conf.status import StatusCode, PARAM_ERROR, HTTP_CONNECT_ERROR, SUCCESS
from aops_agent.manages.token_manage import TokenManage as TOKEN
from aops_agent.tools.util import (
    get_shell_data,
    validate_data,
    get_uuid,
    get_host_ip
)


class Command:

    @classmethod
    def get_host_info(cls) -> dict:
        """
        get basic info about machine

        Returns:
            a dict which contains os version, bios version, kernel version
        """
        os_data = get_shell_data(['cat', '/etc/os-release'], key=False)
        os_version_info = get_shell_data(['grep', 'PRETTY_NAME'], stdin=os_data.stdout)
        os_version = os_version_info.split("=")[1].replace('\n', '').replace('"', '')

        bios_data = get_shell_data(['dmidecode', '-t', '-0'], key=False)
        bios_version_info = get_shell_data(['grep', 'Version'], stdin=bios_data.stdout)
        bios_version = bios_version_info.split(':')[1].replace('\n', '').replace(' ', '')

        kernel_data = get_shell_data(['uname', '-r'])
        kernel_version = kernel_data[:re.search('[a-zA-Z]+', kernel_data).span()[0] - 1]

        host_info = {
            'os': {
                'os_version': os_version,
                'bios_version': bios_version,
                'kernel': kernel_version
            }
        }
        return host_info

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
            if access_token == token:
                return func(*arg, **kwargs)
            res = make_response('token error')
            res.status_code = 401
            return res

        return wrapper

    @classmethod
    def register(cls, register_info: dict) -> str:
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
        except requests.exceptions.ConnectionError:
            return HTTP_CONNECT_ERROR
        ret_data = json.loads(ret.text)
        if ret_data.get('code') == SUCCESS:
            TOKEN.set_value(ret_data.get('token'))
            with open('DEFAULT_TOKEN_PATH', 'w') as f:
                f.write(json.dumps({"access_token": ret_data.get('token')}, indent=4))
            return SUCCESS
        else:
            return ret_data.get('code')
