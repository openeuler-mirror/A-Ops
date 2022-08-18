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
"""
Time: 2022-07-27
Author: YangYunYi
Description: build inventory
"""

import os
import yaml
import pandas

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.join(CURRENT_PATH, "conf")
HOST_INFO_FILE = os.path.join(CONF_PATH, "import_host.xls")
INVENTORY_CONFIG_FILE = os.path.join(CONF_PATH, "inventory_config.yml")
OUTPUT_DIR = "output"


def make_dir(dir_path: str) -> None:
    """
        Make dir if not exist

    Args:
        dir_path(str):

    Returns:
        None
    """
    if not dir_path:
        raise ValueError("dir_path is None")

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def parse_all_dict(file_name: str, component_list: list) -> dict:
    """
        Parse dict of host info

    Args:
        file_name(str): file name of excel
        component_list(list): component list to install

    Returns:
        component_dict_list(dict): component info 
    """
    component_dict_list = dict()
    for component in component_list:
        component_sheet = pandas.read_excel(file_name, sheet_name=component)
        component_dict_list["{}_hosts".format(component)] = {}
        component_dict_list["{}_hosts".format(component)]["hosts"] = {}
        key_list = component_sheet.columns.tolist()
        for index, row in component_sheet.iterrows():
            component_dict_list["{}_hosts".format(component)]["hosts"][row.host_name] = dict()
            for key in key_list:
                if key == "host_name":
                    continue
                component_dict_list["{}_hosts".format(component)]["hosts"][row.host_name][key] = getattr(row, key)
                component_dict_list["{}_hosts".format(component)]["hosts"][row.host_name][
                    "ansible_python_interpreter"] = "/usr/bin/python3"

    return component_dict_list


def dump_to_yaml(component_dict_list:dict, inventory_config_list: dict) ->None:
    """
        Save inventory info to inventory yaml

    Args:
        component_dict_list(dict): host component info 
        inventory_config_list(dict): inventory config list

    Returns:
        None
    """
    make_dir(OUTPUT_DIR)
    for component, component_info in inventory_config_list.items():
        hosts_info_json = dict()
        for host_info in component_info:
            if host_info not in component_dict_list.keys():
                continue
            hosts_info_json[host_info] = component_dict_list.get(host_info)
        inventory_file_path = os.path.join(OUTPUT_DIR, component)
        with open(inventory_file_path, 'w', encoding="utf-8") as inventory_file:
            yaml.dump(hosts_info_json, inventory_file)


def get_inventory() -> None:
    """
        Build inventory file entry

    Args:
        None

    Returns:
        None
    """
    with open(INVENTORY_CONFIG_FILE, "r") as inventory_cfg:
        inventory_config_list = yaml.safe_load(inventory_cfg)
        component_list = list(inventory_config_list.keys())
        component_dict_list = parse_all_dict(HOST_INFO_FILE, component_list)
        dump_to_yaml(component_dict_list, inventory_config_list)


if __name__ == "__main__":
    get_inventory()
