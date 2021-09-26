# coding: utf-8
# !/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description: build Inventory file
Class: InventoryBuilder
"""
import os
import shutil
import yaml
from aops_manager.deploy_manager.ansible_runner.vault_handler import VaultHandler
from aops_manager.deploy_manager.config import INVENTORY_PATH, HOST_VARS_DIR, \
    HOST_VARS_PATH, VAULT_VARS, PLAYBOOK_VARS_PATH
from aops_manager.deploy_manager.utils import build_yaml, make_dir, move_file, copy_dirs
from aops_utils.log.log import LOGGER


class InventoryBuilder:
    """
    Dynamically generating inventory files
    """

    # Host variables that require vault encryption
    vault_vars = VAULT_VARS

    def __init__(self):
        """
        Construct Function
        """
        # Host variables in the inventory host list exist.
        self._host_vars = {}
        # Host variables to be encrypted
        self._vault_host_vars = {}

    def _add_host_vars(self, host_name, vars_key, vars_value, need_vault):
        """
        Add Host Variables
        Args:
            host_name (str): host name
            vars_key (str): Variable name
            vars_value (str): Variable value
            need_vault (bool): Whether encrypted storage is required

        Returns:
            None

        """
        if host_name not in self._host_vars.keys():
            self._host_vars[host_name] = {}
        if not need_vault:
            self._host_vars[host_name][vars_key] = vars_value
            return

        # The plaintext variable file stores var_name:{{vault_var_name}}.
        # The ciphertext variable file plain stores vault_var_name:var_value.
        # The values in the plaintext ciphertext file are transferred through the template {{}}.
        if host_name not in self._vault_host_vars.keys():
            self._vault_host_vars[host_name] = {}
        vault_key_str = "vault_{0}".format(vars_key)
        self._host_vars[host_name][vars_key] = "{{" + "vault_{0}".format(vars_key) + "}}"
        self._vault_host_vars[host_name][vault_key_str] = vars_value

    def _dump_host_vars(self, vault_pwd, dump_path):
        """
        Storing Host Variables to Files
        Args:
            vault_pwd (str): Vault encryption password
            dump_path (str): Whether encrypted storage is required

        Returns:
            None

        """
        for host, host_vars_info in self._host_vars.items():
            host_vars_path = os.path.join(dump_path, HOST_VARS_DIR, host)
            make_dir(host_vars_path)

            host_vars_plain = os.path.join(host_vars_path, "plain")
            build_yaml(host_vars_plain, host_vars_info)

        for host, host_vars_info in self._vault_host_vars.items():
            host_vars_path = os.path.join(dump_path, HOST_VARS_DIR, host)
            make_dir(host_vars_path)

            host_vars_vault = os.path.join(host_vars_path, "crypted")
            vault_handler = VaultHandler(vault_pwd)
            yaml_str = yaml.dump(host_vars_info)
            vault_yaml_bytes = vault_handler.encrypt_string(yaml_str)
            with open(host_vars_vault, "w", encoding="utf-8") as file:
                file.write(vault_yaml_bytes.decode())

    @staticmethod
    def move_host_vars_to_inventory(src_path, host_name):
        """
        Move inventory files to "ansible_handler/inventory/host_vars"
        Args:
            src_path (str): Directory where files are currently stored
            host_name (str): host dir name in host_vars

        Returns:
            None

        Raise:
            ValueError
        """
        if not all([src_path, host_name]):
            raise ValueError("Invalid parameters of src_path, host_name")
        src_inventory_path = os.path.join(src_path, host_name)
        if not os.path.exists(src_inventory_path):
            LOGGER.debug("HOST_VARS_PATH %s is not existed", src_inventory_path)
            return
        ansible_inventory_path = os.path.join(HOST_VARS_PATH, host_name)
        LOGGER.debug("move_host_vars_to_inventory from %s to %s",
                     src_path, ansible_inventory_path)
        copy_dirs(src_inventory_path, ansible_inventory_path)

    @staticmethod
    def remove_host_vars_in_inventory():
        """
        Remove host vars files in "ansible_handler/inventory/host_vars" after a task executed
        """
        if not os.path.exists(HOST_VARS_PATH):
            LOGGER.debug("HOST_VARS_PATH %s is not existed", HOST_VARS_PATH)
            return
        shutil.rmtree(HOST_VARS_PATH)

    @staticmethod
    def remove_specified_host_vars(host_name_list, host_vars_path):
        """
        Delete the host_vars directory of a host (host_name) in
        a specified directory (host_vars_path).
        Args:
            host_name_list (list): host name is the name of the host's vars dir
            host_vars_path (str): the host_vars path

        Returns:
            None
        """
        for hots_name in host_name_list:
            host_vars_dir = os.path.join(host_vars_path, "host_vars", hots_name)
            if not os.path.exists(host_vars_dir):
                LOGGER.debug("HOST_VARS_PATH %s is not existed", host_vars_dir)
                continue
            shutil.rmtree(host_vars_dir)


    @staticmethod
    def move_host_to_inventory(inventory_file_path, file_name):
        """
        Move inventory files to "ansible_handler/inventory/"
        Args:
            inventory_file_path (str): Directory where files are currently stored
            file_name (str): inventory file name

        Returns:
            None

        Raise:
            ValueError
        """
        if not all([inventory_file_path, file_name]):
            raise ValueError("Invalid parameters of inventory_file_path, file_name")

        make_dir(INVENTORY_PATH)
        LOGGER.debug("move_host_vars_to_inventory file_name %s from %s to %s",
                     file_name, inventory_file_path, INVENTORY_PATH)
        move_file(inventory_file_path, INVENTORY_PATH, file_name)

    @staticmethod
    def move_playbook_vars_to_inventory(vars_file_path, file_name):
        """
        Move inventory files to "ansible_handler/vars"
        Args:
            vars_file_path (str): Directory where playbook vars files are currently stored
            file_name (str): the file name of playbook vars

        Returns:
            None

        Raises:
            ValueError
        """
        if not all([vars_file_path, file_name]):
            raise ValueError("Invalid parameters of vars_file_path, file_name")

        make_dir(PLAYBOOK_VARS_PATH)
        LOGGER.debug("move_playbook_vars_to_inventory file_name %s from %s to %s",
                     file_name, vars_file_path, PLAYBOOK_VARS_PATH)
        move_file(vars_file_path, PLAYBOOK_VARS_PATH, file_name)

    @staticmethod
    def _dump_inventory(hosts_info_json, dump_path, inventory_file_name):
        """
        Storage Host Inventory to File in "ansible_handler/inventory/host_vars"
        Args:
            hosts_info_json (dict): hosts info in json
            dump_path (str): Directory where files are currently stored
            inventory_file_name (str): Host Inventory File Name

        Returns:
            None

        """
        make_dir(dump_path)
        inventory_file_path = os.path.join(dump_path, inventory_file_name)
        with open(inventory_file_path, 'w', encoding="utf-8") as inventory_file:
            yaml.dump(hosts_info_json, inventory_file)

    def import_host_list(self, hosts_info_json, inventory_file_name, dump_path):
        """
        Import host list
        Args:
            hosts_info_json (dict): hosts info in json, format are as follow:
                {
                    "group_info": {
                        "host_name": {
                            "ansible_host": "192.168.1.1",
                            "var1": value1,
                            "var2": "value2"
                            ...
                        },
                        ...
                    },
                    ...
                }
            dump_path (str): Directory where files are currently stored
            inventory_file_name (str): Host Inventory File Name

        Returns:
            None

        Raise:
            ValueError
        """
        if not all([hosts_info_json, inventory_file_name, dump_path]):
            raise ValueError("Invalid parameters of hosts_info_json, "
                             "inventory_file_name, dump_path")
        inventory_json = {}
        for group_name, group_info in hosts_info_json.items():
            inventory_json[group_name] = {"hosts": {}}
            for host_name, host_info in group_info.items():
                inventory_json[group_name]["hosts"][host_name] = {}
                for var_name, var_value in host_info.items():
                    inventory_json[group_name]["hosts"][host_name][var_name] = var_value

        self._dump_inventory(inventory_json, dump_path, inventory_file_name)

    def import_host_vars(self, hosts_info_json, vault_pwd, dump_path):
        """
        Import host list
        Args:
            hosts_info_json (dict): hosts info in json, format are as follow:
                {
                    "group_info": {
                        "host_name": {
                            "ansible_user": "aops",
                            "ansible_ssh_pass": "xxx",
                            "ansible_become_user": "root",
                            "ansible_become_method": "su",
                            "ansible_become_password": "xxxxx"
                        },
                        ...
                    }
                }
            vault_pwd (str): Encrypt the vault password of the host variable.
            dump_path (str): Directory where files are currently stored

        Returns:
            None

        Raise:
            ValueError
        """
        if not all([hosts_info_json, vault_pwd, dump_path]):
            raise ValueError("Invalid parameters of hosts_info_json, "
                             "inventory_file_name, dump_path")
        for group_info in hosts_info_json.values():
            for host_name, host_info in group_info.items():
                for var_name, var_value in host_info.items():
                    need_vault = bool(var_name in self.vault_vars)
                    self._add_host_vars(host_name, var_name, var_value, need_vault)

        self._dump_host_vars(vault_pwd, dump_path)
