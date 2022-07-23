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
import configparser
import os


def load_conf(file_path: str) -> configparser.RawConfigParser:
    """
    get ConfigParser object when loads config file
    for example: XX.service

    Returns:
        ConfigParser object
    """
    cf = configparser.RawConfigParser()
    if os.path.exists(file_path):
        cf.read(file_path, encoding='utf8')
    if cf.sections:
        return cf
    raise Exception('file not found or the contents of the file are incorrect.')
