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
Description: Restful APIs for host
"""
import os
import uuid
from flask import request
from flask import jsonify
from flask_restful import Resource
import yaml

from aops_manager.function.verify.config import CollectConfigSchema
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.deploy_manager.run_task import TaskRunner
from aops_manager.account_manager.key import HostKey
from aops_manager.conf import configuration
from aops_utils.conf.constant import DATA_GET_HOST_INFO
from aops_utils.log.log import LOGGER
from aops_utils.restful.helper import make_datacenter_url
from aops_utils.restful.status import StatusCode, PARAM_ERROR, SUCCEED, KEY_ERROR, PARTIAL_SUCCEED
from aops_utils.restful.response import MyResponse
from aops_utils.restful.serialize.validate import validate


def traversal_ansible_output(status, **kwargs):
    """
    traversal ansible output list
    Args:
        kwargs(dict):
            infos(list): host info get from database
            success_files(list): success files list
            fail_files(list): fail files list
            info(dict): host info from infos
            res_data(list): success list, skipped list of the ansible output
        status(str): success or skipped list

    """
    info = kwargs.get('info')
    res_data = kwargs.get('res_data')
    fail_files = kwargs.get('fail_files')
    success_files = kwargs.get('success_files')
    infos = kwargs.get('infos')
    public_ip = str(info['public_ip'])
    path = os.path.join('/home/dest/', public_ip)
    if not res_data[status]:
        return
    for host in res_data[status].keys():
        if host != public_ip:
            continue
        host_res = res_data[status][host]
        if host_res['task_name'] == "Check that if the file exists":
            continue
        for res_file in host_res['result']['results']:
            file_dict = {}
            if not res_file['item']['stat']['exists']:
                fail_files.append(res_file['item']['invocation']['module_args']['path'])
                continue
            file_dict['path'] = res_file['item']['stat']['path']
            success_files.append(file_dict['path'])
            file_dict['file_attr'] = {}
            file_dict['file_attr']['mode'] = res_file['item']['stat']['mode']
            file_dict['file_attr']['owner'] = res_file['item']['stat']['pw_name']
            file_dict['file_attr']['group'] = res_file['item']['stat']['gr_name']
            with open(path + file_dict['path'], 'r', encoding='utf-8') as file_conf:
                file_dict['content'] = ""
                for line in file_conf.readlines():
                    file_dict['content'] += line
            os.remove(path + file_dict['path'])
            infos.append(file_dict)


def generate_output(host_infos):
    """
    generate output file to the request
    Args:
        host_infos(list): host infos get from database

    Returns:
        dict:
            {
                "succeed_list": succeed_list,
                "fail_list": fail_list,
                "resp": resp_list,
                "is_par": is_par
            }
    """
    succeed_list = []
    fail_list = []
    resp_list = []
    is_par = False
    res, res_data = TaskRunner.run_playbook('read_config',
                                            "read_config",
                                            HostKey.key)
    task_id = str(uuid.uuid1()).replace('-', '')
    if res:
        succeed_list.append(task_id)
        LOGGER.info("task %s execute succeed", task_id)
    else:
        fail_list.append(task_id)
        LOGGER.warning("task %s execute fail", task_id)
        return {}

    for info in host_infos:
        host_id_dict = {'host_id': info['host_id']}
        infos = []
        success_files = []
        fail_files = []

        args_dict = {
            "res_data": res_data,
            "info": info,
            "fail_files": fail_files,
            "success_files": success_files,
            "infos": infos
        }
        traversal_ansible_output(status="success", **args_dict)
        traversal_ansible_output(status="skipped", **args_dict)
        host_id_dict['infos'] = infos
        host_id_dict['success_files'] = success_files
        host_id_dict['fail_files'] = fail_files
        if len(success_files) > 0 and len(fail_files) > 0:
            is_par = True
        resp_list.append(host_id_dict)

    return {"succeed_list": succeed_list,
            "fail_list": fail_list,
            "resp": resp_list,
            "is_par": is_par}


def generate_ansible_input_json(host_infos, inventory, params):
    """
    function to generate ansible input json file
    Args:
        host_infos(list): host infos get from database
        inventory(InventoryBuilder): Inventory class
        params(dict):  params of the requests

    Returns:

    """
    ansible_input_json = {'read_config_hosts': {}}
    for info in host_infos:

        # move host dir to vars
        inventory.move_host_vars_to_inventory(configuration.manager.get('HOST_VARS'),
                                              str(info['public_ip']))

        # read_config.json generate
        ansible_input_json_host = {'ansible_host': info['public_ip'],
                                   'ansible_python_interpreter': '/usr/bin/python3',
                                   'config_list': []}
        for item in params['infos']:
            if item['host_id'] == info['host_id']:
                for config in item['config_list']:
                    ansible_input_json_host['config_list'] \
                        .append({"src": config, "dest": "/home/dest"})
                break
        ansible_input_json['read_config_hosts'][info['public_ip']] = ansible_input_json_host
    return ansible_input_json


def generate_yaml_vars():
    """
    generate yaml vars
    """
    # generate_read_config_vars.yaml
    yaml_init = {}
    ymlpath = os.path.join('/tmp/', "read_config_vars.yml")
    with open(ymlpath, 'w', encoding="utf-8") as file:
        yaml.dump(yaml_init, file)


def read_yaml_data(yaml_file):
    """
    read yaml file.

    Args:
        yaml_file:  yaml file

    Returns:
        dict: yaml content of the yaml file
    """
    with open(yaml_file, 'r', encoding="utf-8") as file:
        file_data = file.read()

    data = yaml.safe_load(file_data)
    return data


class CollectConfig(Resource):
    """
    Interface for collect config.
    Restful API: POST
    """

    @staticmethod
    def post():
        """
        Get config

        Args:
            request(json): {
                    "infos": [
                        {
                            "host_id": "f",
                            "config_list": ["/xx", "/exxxo"]
                        },
                        {
                            "host_id": "f",
                            "config_list": ["/exc/hoxxame"]
                        }
                    ]
            }

        Returns:
            dict: response body
        """
        args = request.get_json()
        params, errors = validate(CollectConfigSchema, args, load=True)
        if errors:
            response = StatusCode.make_response(PARAM_ERROR)
            return jsonify(response)
        LOGGER.debug(params)
        if HostKey.key == "":
            response = StatusCode.make_response(KEY_ERROR)
            return jsonify(response)
        # Arrange params to data_get_host_info
        host_list = []
        for host in params['infos']:
            host_list.append(host['host_id'])

        pyload = {
            "host_list": host_list,
            "basic": True,
            "username": "admin"
        }
        # make database center url
        database_url = make_datacenter_url(DATA_GET_HOST_INFO)
        response = MyResponse.get_response("POST", database_url, pyload)
        if response.get('code') != SUCCEED:
            return LOGGER.error("Request database failed")
        inventory = InventoryBuilder()
        ansible_input_json = generate_ansible_input_json(response['host_infos'],
                                                         inventory,
                                                         params)
        # json to yaml and move to
        inventory_operate(ansible_input_json, inventory)
        final_res = generate_output(response['host_infos'])
        is_par = final_res.get("is_par")
        if not is_par:
            response = StatusCode.make_response(SUCCEED)
        else:
            response = StatusCode.make_response(PARTIAL_SUCCEED)
        response['succeed_list'] = final_res.get("succeed_list")
        response['fail_list'] = final_res.get("fail_list")
        response['resp'] = final_res.get("resp")
        return jsonify(response)


def inventory_operate(ansible_input_json, inventory):
    """
    inventory files' operation
    Args:
        ansible_input_json(json): json file of hosts
        inventory(class): InvenoryBuild Class include inventories' methods

    Returns:

    """
    inventory.import_host_list(ansible_input_json, "read_config", '/tmp')
    inventory.move_host_to_inventory('/tmp', 'read_config')
    generate_yaml_vars()
    inventory.move_playbook_vars_to_inventory('/tmp', 'read_config_vars.yml')
