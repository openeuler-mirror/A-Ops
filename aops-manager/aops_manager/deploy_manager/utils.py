# coding: utf-8
# !/usr/bin/python3
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
Description: General functions
"""
import os
import shutil
import yaml
from aops_utils.log.log import LOGGER

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


def build_yaml(file_path, yaml_obj):
    """
    Creates a YAML file based on the YAML object.
    Args:
        file_path (str): YAML file path
        yaml_obj (dict): yaml obj in json

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as yaml_file:
        yaml.dump(yaml_obj, yaml_file)


def make_dir(dir_path):
    """
    Creating a File Directory
    Args:
        dir_path (str): dir path

    Returns:
        None

    Raise:
        ValueError
    """
    if not dir_path:
        raise ValueError("dir_path is None")

    is_file_existed = os.path.exists(dir_path)

    if not is_file_existed:
        os.makedirs(dir_path)
        LOGGER.debug("make new path %s", dir_path)
    else:
        LOGGER.debug("path %s existed.", dir_path)


def copy_dirs(src_path, dst_path):
    """
    Copy a File Directory
    Args:
        src_path (str): source dir path
        dst_path (str): destination dir path

    Returns:
        None

    Raise:
        ValueError
    """
    if not all([src_path, dst_path]):
        raise ValueError("dir_path is None")

    if not os.path.exists(dst_path):
        # Create a folder if the original folder does not exist in the target path.
        os.makedirs(dst_path)

    if os.path.exists(dst_path):
        # If the original folder exists in the target path, delete it first.
        shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path)


def move_file(src_path, dst_path, file):
    """
    Moving a File
    Args:
        src_path (str): source dir path
        dst_path (str): destination dir path
        file (str): the file to be moved

    Returns:
        None
    """
    src_file = os.path.join(src_path, file)
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    dst_file = os.path.join(dst_path, file)
    shutil.move(src_file, dst_file)
