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
Constant variable oof deploy manager
"""
import os

VAULT_VARS = ["ansible_user", "ansible_ssh_pass",
              "ansible_become_user", "ansible_become_pass"]

HOST_VARS_DIR = "host_vars"
# current file path
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
# ansible_handler/playbooks
PLAYBOOK_PATH = os.path.join(CURRENT_PATH, "ansible_handler", "playbooks")
# ansible_handler/inventory
INVENTORY_PATH = os.path.join(CURRENT_PATH, "ansible_handler", "inventory")
# ansible_handler/inventory/host_vars
HOST_VARS_PATH = os.path.join(INVENTORY_PATH, HOST_VARS_DIR)
# ansible_handler/vars/
PLAYBOOK_VARS_PATH = os.path.join(CURRENT_PATH, "ansible_handler", "vars")
# tasks/
TASKS_PATH = os.path.join(CURRENT_PATH, "tasks")
