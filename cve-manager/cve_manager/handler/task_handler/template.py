#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: playbook template
"""
COPY_SCRIPT_TEMPLATE = {
    'hosts': 'total_hosts',
    'gather_facts': False,
    'tasks': [
        {
            'name': 'copy script',
            'become': True,
            'become_user': 'root',
            'copy': {
                    'src': 'check.sh',
                    'dest': '/tmp/check.sh',
                    'owner': 'root',
                    'group': 'root',
                    'mode': 'a+x'
            }
        }
    ]
}


REBOOT_TEMPLATE = {
    'hosts': 'reboot_hosts',
    'gather_facts': False,
    'tasks': [
        {
            'name': 'reboot',
            'become': True,
            'become_user': 'root',
            'shell': 'reboot'
        }
    ]
}
