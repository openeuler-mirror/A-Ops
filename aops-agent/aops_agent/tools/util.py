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
from typing import Union, List, Any
from subprocess import Popen, PIPE, STDOUT

from flask import Response, make_response
from jsonschema import validate, ValidationError
from aops_agent.conf.constant import DATA_MODEL
from aops_agent.models.custom_exception import InputError


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


def get_shell_data(command_list: List[str], key: bool = True, stdin: Popen = None) -> Union[str, Popen]:
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
    schema = DATA_MODEL.get('list_str')
    if validate_data(command_list, schema) is False:
        raise InputError('please check your command')
    try:
        res = Popen(command_list, stdout=PIPE, stdin=stdin, stderr=STDOUT)
    except FileNotFoundError as e:
        raise InputError('linux has no command') from e
    if key:
        return res.stdout.read().decode()
    return res


def create_response(status_code: int, msg: str) -> Response:
    """
        Construct the response body

    Args:
        status_code (int): http status code
        msg (str): message which you want to tell

    Returns:
        Response body
    """
    rsp = make_response(msg)
    rsp.status_code = status_code
    return rsp
