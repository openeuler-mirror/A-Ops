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
import uuid
from collections import defaultdict
from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_manager.function.verify.host import AddHostSchema, HostSchema,\
    DeleteHostSchema, GetHostSchema, AddHostGroupSchema, DeleteHostGroupSchema,\
    GetHostGroupSchema, GetHostInfoSchema
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.conf import configuration
from aops_utils.conf.constant import DATA_ADD_HOST, DATA_DELETE_HOST, DATA_GET_HOST,\
    DATA_ADD_GROUP, DATA_DELETE_GROUP, DATA_GET_GROUP, DATA_GET_HOST_COUNT, DATA_GET_HOST_INFO
from aops_utils.restful.status import PARAM_ERROR, SUCCEED, StatusCode
from aops_utils.restful.response import MyResponse
from aops_utils.restful.serialize.validate import validate
from aops_utils.restful.helper import make_datacenter_url


class AddHost(Resource):
    """
    Interface for add host.
    Restful API: post
    """

    def post(self):
        """
        Add host

        Args:
            host_list(list)
            key(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(args, AddHostSchema, access_token)
        if verify_res != SUCCEED:
            response = StatusCode.make_response(verify_res)
            return jsonify(response)

        host_vault = defaultdict(dict)
        host_list = []
        host_id_list = []

        for host_info in args.get('host_list'):
            # verify the params
            info, errors = validate(HostSchema, host_info)
            if errors:
                response = StatusCode.make_response(PARAM_ERROR)
                response['wrong_info'] = host_info
                return jsonify(response)
            # generate uuid of the host
            host_id = str(uuid.uuid1()).replace('-', '')
            host_id_list.append(host_id)
            info['host_id'] = host_id
            host_vault[info['host_group_name']][info['host_name']] =\
                self._generate_host_var(info)
            host_list.append(info)

        args['host_list'] = host_list
        # make database center url
        database_url = make_datacenter_url(DATA_ADD_HOST)
        response = MyResponse.get_response("post", database_url, args)

        if response["code"] == SUCCEED:
            response['host_list'] = host_id_list
            # then encrypt password
            inventory = InventoryBuilder()
            inventory.import_host_vars(
                host_vault, args['key'], configuration.manager['HOST_VAULT_DIR']) # pylint: disable=E1101

        return jsonify(response)

    @staticmethod
    def _generate_host_var(host_info):
        """
        Generate host var

        Args:
            host_info(dict): host info

        Returns:
            dict
        """
        result = dict()
        result['ansible_user'] = host_info['username']
        result['ansible_ssh_pass'] = host_info['password']
        result['ansible_ssh_port'] = host_info['ssh_port']
        result['ansible_become_user'] = 'root'
        result['ansible_become_method'] = 'su'
        result['ansible_become_pass'] = host_info['sudo_password']

        host_info.pop('username')
        host_info.pop('password')
        host_info.pop('sudo_password')

        return result


class DeleteHost(Resource):
    """
    Interface for delete host.
    Restful API: DELETE
    """
    @staticmethod
    def delete():
        """
        Delete host

        Args:
            host_list(list): host id list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_HOST)
        verify_res = MyResponse.verify_all(
            args, DeleteHostSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'delete', database_url, args)
        succeed_list = response.get('succeed_list')
        host_name_list = []
        if succeed_list:
            host_info = response.pop('host_info')
            for host_id in succeed_list:
                host_name_list.append(host_info[host_id])
            inventory = InventoryBuilder()
            inventory.remove_specified_host_vars(
                host_name_list, configuration.manager['HOST_VAULT_DIR'])

        return jsonify(response)


class GetHost(Resource):
    """
    Interface for get host.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Get host

        Args:
            host_group_list(list): host group name list
            management(bool): whether it's a manage node
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_HOST)
        verify_res = MyResponse.verify_all(args, GetHostSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class GetHostCount(Resource):
    """
    Interface for get host count.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Get host

        Args:

        Returns:
            dict: response body
        """
        args = {}
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_HOST_COUNT)
        verify_res = MyResponse.verify_token(access_token, args)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class AddHostGroup(Resource):
    """
    Interface for add host group.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Add host group

        Args:
            host_group_name(str): group name
            description(str): group description

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_ADD_GROUP)
        verify_res = MyResponse.verify_all(
            args, AddHostGroupSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class DeleteHostGroup(Resource):
    """
    Interface for delete host group.
    Restful API: DELETE
    """
    @staticmethod
    def delete():
        """
        Delete host group

        Args:
            host_group_list(list): group name list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_GROUP)
        verify_res = MyResponse.verify_all(
            args, DeleteHostGroupSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'delete', database_url, args)

        return jsonify(response)


class GetHostGroup(Resource):
    """
    Interface for get host group.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Get host group

        Args:
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_GROUP)
        verify_res = MyResponse.verify_all(
            args, GetHostGroupSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class GetHostInfo(Resource):
    """
    Interface for get host info.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Get host info

        Args:
            host_list(list): host id list
            basic(bool)

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_HOST_INFO)
        verify_res = MyResponse.verify_all(
            args, GetHostInfoSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)
