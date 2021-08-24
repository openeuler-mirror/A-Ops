#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description:
"""
import xml
import json
import xmltodict
import yaml

from aops_utils.validate import validate_path
from aops_utils.log.log import LOGGER


def read_yaml_config_file(config_file):
    """
    Read yaml configuration file.

    Args:
        config_file (str): the configuration file path

    Returns:
        dict/None
    """
    conf = None
    if config_file is None:
        return conf

    if validate_path(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as file_io:
                conf = yaml.safe_load(file_io.read())
                if not isinstance(conf, (dict, list)):
                    LOGGER.error(
                        "YAML [%s] didn't produce a dictionary or list.", config_file)
                    conf = None
        except yaml.scanner.ScannerError:
            LOGGER.error("Couldn't parse yaml %s ", config_file)

    return conf


def read_json_config_file(config_file):
    """
    Read json configuration file.

    Args:
        config_file (str): the configuration file path

    Returns:
        dict/None
    """
    conf = None
    if config_file is None:
        return conf

    if validate_path(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as file_io:
                conf = json.load(file_io)
        except json.decoder.JSONDecodeError as error:
            LOGGER.error('%s in %s', str(error), config_file)

    return conf


def read_xml_config_file(config_file):
    """
    Read xml configuration file.

    Args:
        config_file (str): the configuration file path

    Returns:
        dict/None
    """
    conf = None
    if config_file is None:
        return conf

    if validate_path(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as file_io:
                xml_parse = xmltodict.parse(file_io.read())
                conf = json.loads(json.dumps(xml_parse))
        except xml.parsers.expat.ExpatError:
            LOGGER.error('%s parsed failed.', config_file)

    return conf
