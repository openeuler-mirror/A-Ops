#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: running task runner
"""

from aops_manager.deploy_manager.ansible_runner.ansible_runner import AnsibleRunner


def test_command():
    ansible_runner = AnsibleRunner('/etc/ansible/hosts', "11765421")
    ansible_runner.run('all', 'shell', "ping baidu.com -c 2 >/tmp/ping.txt")
    print(ansible_runner.get_result())


def test_playbook():
    ansible_runner = AnsibleRunner('/etc/ansible/hosts', "11765421")
    ansible_runner.run_playbook("test.yaml")
    print(ansible_runner.get_result())


if __name__ == "__main__":
    test_command()
    test_playbook()
