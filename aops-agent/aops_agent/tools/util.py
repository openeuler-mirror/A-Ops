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
import os
from typing import Union, List, Any, Tuple
from subprocess import Popen, PIPE, STDOUT

from libconf import load, ConfigParseError, AttrDict
from flask import Response, make_response
from jsonschema import validate, ValidationError
from aops_agent.conf.constant import DATA_MODEL, RPM_INFO
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


def create_response(status_code: int, data: str) -> Response:
    """
        Construct the response body

    Args:
        status_code (int): http status code
        data (str): json data

    Returns:
        Response body
    """
    rsp = make_response(data)
    rsp.status_code = status_code
    return rsp


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


def plugin_install_judge(plugin_name: str) -> str:
    """
    judge if the plugin is installed

    Args:
        plugin_name(str)

    Returns:
        str: plugin running status
    """
    rpm_name = RPM_INFO.get(plugin_name, "")
    status_info = get_shell_data(["systemctl", "status", rpm_name], key=False)
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
