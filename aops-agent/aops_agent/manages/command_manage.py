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

import connexion
from flask import make_response

from aops_agent.manages.token_manage import TokenManage as TOKEN
from aops_agent.tools.util import get_shell_data


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
