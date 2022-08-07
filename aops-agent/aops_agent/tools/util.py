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
import copy
import json
import os
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Union, List, Any, Tuple, Dict, NoReturn
from subprocess import Popen, PIPE, STDOUT

from libconf import load, ConfigParseError, AttrDict
from flask import Response, make_response
from jsonschema import validate, ValidationError
from aops_agent.conf.constant import DATA_MODEL, INFORMATION_ABOUT_RPM_SERVICE
from aops_agent.log.log import LOGGER
from aops_agent.models.custom_exception import InputError


def load_conf(file_path: str) -> configparser.RawConfigParser:
    """
    get ConfigParser object when loads config file
    for example: XX.service

    Returns:
        ConfigParser object
    """
    cf = configparser.RawConfigParser()
    try:
        cf.read(file_path, encoding='utf8')
    except FileNotFoundError:
        LOGGER.error('file not found')
    return cf


def validate_data(data: Any, schema: dict) -> bool:
    """
    validate data type which is expected

    Args:
        data (object): which need to validate
        schema (dict): expected data model

    Returns:
        bool

    Raises:
        ValidationError: the data structure isn't we expected
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False


def get_shell_data(command_list: List[str],
                   key: bool = True, stdin: Popen = None) -> Union[str, Popen]:
    """
    execute shell commands

    Args:
        command_list( List[str] ): a list containing the command arguments.
        key (bool): Boolean value
        stdin (Popen): Popen object

    Returns:
        get str result when execute shell command success and the key is True or
        get Popen object when execute shell command success and the key is False

    Raises:
        FileNotFoundError: linux has no this command
    """
    schema = DATA_MODEL.get('str_array')
    if validate_data(command_list, schema) is False:
        raise InputError('please check your command')
    try:
        res = Popen(command_list, stdout=PIPE, stdin=stdin, stderr=STDOUT)
    except FileNotFoundError as e:
        raise InputError('linux has no command') from e
    if key:
        return res.stdout.read().decode()
    return res


def load_gopher_config(gopher_config_path: str) -> AttrDict:
    """
    get AttrDict from config file

    Args:
        gopher_config_path(str)

    Returns:
       AttrDict: a subclass of `dict`that exposes string keys as attributes
    """
    try:
        with open(gopher_config_path, 'r', encoding='utf8') as file:
            cfg = load(file)
    except FileNotFoundError:
        LOGGER.error('gopher config not found')
        return AttrDict()
    except ConfigParseError:
        LOGGER.error('gopher config file corrupted')
        return AttrDict()
    return cfg


def plugin_status_judge(plugin_name: str) -> str:
    """
    judge if the plugin is installed

    Args:
        plugin_name(str)

    Returns:
        str: plugin running status
    """
    if plugin_name in INFORMATION_ABOUT_RPM_SERVICE.keys():
        service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name).get('service_name')
        if service_name is None:
            return ""
    else:
        return ""
    status_info = get_shell_data(["systemctl", "status", service_name], key=False)
    res = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
    return res


def change_probe_status(probes: Tuple[AttrDict], gopher_probes_status: dict, res: dict) -> Tuple:
    """
    to change gopher probe status

    Args:
        res(dict): which contains status change success list
        probes(Tuple[AttrDict]): gopher probes info
        gopher_probes_status(dict): probe status which need to change

    Returns:
        Tuple which contains change successful plugin and change fail plugin
    """
    failure_list = copy.deepcopy(gopher_probes_status)
    for probe in probes:
        if probe.get('name', "") in gopher_probes_status:
            probe['switch'] = gopher_probes_status[probe['name']]
            res['success'].append(probe['name'])
            failure_list.pop(probe['name'])
    return res, failure_list


def get_uuid() -> str:
    """
        get uuid about disk

    Returns:
        uuid(str)
    """
    fstab_info = get_shell_data(['dmidecode'], key=False)
    uuid_info = get_shell_data(['grep', 'UUID'], stdin=fstab_info.stdout)
    uuid = uuid_info.replace("-", "").split(':')[1].strip()
    return uuid


def get_host_ip() -> str:
    """
        get host ip by create udp package
    Returns:
        host ip(str)
    """
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.connect(('8.8.8.8', 80))
        host_ip = sock.getsockname()[0]
    except OSError:
        LOGGER.error("please check internet")
        host_ip = ''
    finally:
        sock.close()
    return host_ip


def get_dict_from_file(file_path: str) -> Dict:
    """
        Get json data from file and return related dict
    Args:
        file_path(str): the json data file absolute path

    Returns:
        dict(str)
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        LOGGER.error('file not found')
        data = {}
    except json.decoder.JSONDecodeError:
        LOGGER.error('file structure is not json')
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data


def register_info_to_dict(string: str) -> Dict:
    """
    Convert JSON string to dictionary
    Args:
        string(str)

    Returns:
        dict
    """
    try:
        res = json.loads(string)
    except json.decoder.JSONDecodeError:
        LOGGER.error('Parameter error')
        res = {}
    if not isinstance(res, dict):
        res = {}
    return res


def save_data_to_file(data: str, file_path: str, mode: str = 'w', encoding: str = 'utf-8') -> NoReturn:
    """
        save data to specified path,create it if it doesn't exist

    Args:
        data:
        file_path(str): file absolute path
        mode(str): select write mode, default 'w'
        encoding(str): select encoding mode, default utf8
    """
    file_dir_path = os.path.dirname(file_path)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)
    with open(file_path, mode=mode, encoding=encoding) as f:
        f.write(data)


def update_ini_data_value(file_path: str, section: str, option: str, value) -> NoReturn:
    """
    modify or create an option
    Args:
        file_path(str): file absolute path
        section(str):   section name
        option(str):    option name
        value(str)      section value


    """
    cf = configparser.ConfigParser()
    try:
        cf.read(file_path, encoding='utf8')
    except FileNotFoundError:
        LOGGER.error('agent config file has benn deleted')
    except configparser.MissingSectionHeaderError:
        LOGGER.error('agent config file has benn damaged')
    except configparser.ParsingError:
        LOGGER.error('agent config file has benn damaged')
    file_dir_path = os.path.dirname(file_path)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)
    cf[section] = {option: value}
    with open(file_path, 'w') as f:
        cf.write(f)
