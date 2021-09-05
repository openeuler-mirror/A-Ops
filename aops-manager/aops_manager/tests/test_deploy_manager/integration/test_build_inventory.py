#!/usr/bin/python3
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
Description: Running Deployment Tasks
Class: TaskRunner
"""
import os
import shutil
import argparse
import json
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.deploy_manager.config import HOST_VARS_DIR
from aops_utils.log.log import LOGGER

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
HOST_LIST_DIR = "host_list"
HOST_VAULT_JSON = "host_vault.json"
TMP_PATH = "tmp"


def build_inventory(host_list_file, inventory_file_name, dump_dir):
    """
    Combine the current directory, subdirectory, and file name to generate the file path.
    Args:
        host_list_file: JSON file for storing host list information
        inventory_file_name: Generated inventory file
        dump_dir: Relative path of the inventory file

    Returns:
        None
    """
    with open(host_list_file, 'r', encoding="utf-8") as load_file:
        print(load_file)
        load_dict = json.load(load_file)
        inventory_builder = InventoryBuilder()
        dump_path = os.path.join(CURRENT_PATH, dump_dir)
        inventory_builder.import_host_list(
            load_dict, inventory_file_name, dump_path)
        LOGGER.debug("build_inventory in dump_path %s, inventory_file_name %s",
                     dump_path, inventory_file_name)


def build_host_vars(host_list_file, vault_pwd, dump_dir):
    """
    Combine the current directory, subdirectory, and file name to generate the file path.
    Args:
        host_list_file: JSON file for storing host list information
        vault_pwd: Vault encryption password
        dump_dir: Relative path of the inventory file

    Returns:
        None
    """
    with open(host_list_file, 'r', encoding="utf-8") as load_file:
        load_dict = json.load(load_file)
        inventory_builder = InventoryBuilder()
        dump_path = os.path.join(CURRENT_PATH, dump_dir)
        inventory_builder.import_host_vars(
            load_dict, vault_pwd, dump_path)


def get_all_host_list():
    """
    Obtaining the List of All Hosts

    Returns:
        None
    """
    host_list_path = os.path.join(CURRENT_PATH, HOST_LIST_DIR)
    files_list = os.listdir(host_list_path)
    for file in files_list:
        host_file = os.path.join(host_list_path, file)
        host_file_name = file.split(".")[0]
        LOGGER.debug("Get %s host list %s", host_file_name, host_file)
        build_inventory(host_file, host_file_name, TMP_PATH)
        inventory_file_path = os.path.join(CURRENT_PATH, TMP_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--build', type=str, default=None)
    parser.add_argument('--move', type=str, default=None)
    args = parser.parse_args()
    LOGGER.debug("Start run build %s, move %s", args.build, args.move)

    # Executing a Deployment Task
    if args.build == "host_vars":
        host_vault_file = os.path.join(CURRENT_PATH, HOST_LIST_DIR, HOST_VAULT_JSON)
        # build_host_vars(host_vault_file, "test", TMP_PATH) 11765421
        build_host_vars(host_vault_file, "11765421", TMP_PATH)
    elif args.build == "host":
        get_all_host_list()
    elif args.build == "all":
        host_vault_file = os.path.join(CURRENT_PATH, HOST_LIST_DIR, HOST_VAULT_JSON)
        build_host_vars(host_vault_file, "11765421", TMP_PATH)
        get_all_host_list()

    if args.move == "host_vars":
        host_vars_path = os.path.join(CURRENT_PATH, TMP_PATH, HOST_VARS_DIR)
        for root, dirs, files in os.walk(host_vars_path):
            for host_name in dirs:
                InventoryBuilder.move_host_vars_to_inventory(host_vars_path, host_name)

    elif args.move == "host":
        tmp_file_path = os.path.join(CURRENT_PATH, TMP_PATH)
        shutil.rmtree(tmp_file_path)
    elif args.move == "all":
        host_vars_path = os.path.join(CURRENT_PATH, TMP_PATH, HOST_VARS_DIR)
        for root, dirs, files in os.walk(host_vars_path):
            for host_name in dirs:
                InventoryBuilder.move_host_vars_to_inventory(host_vars_path, host_name)

        tmp_file_path = os.path.join(CURRENT_PATH, TMP_PATH)
        shutil.rmtree(tmp_file_path)
