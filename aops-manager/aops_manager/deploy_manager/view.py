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
import uuid
from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import StatusCode, SUCCEED, PARAM_ERROR
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_datacenter_url
from aops_utils.conf.constant import DATA_ADD_TASK, DATA_ADD_TEMPLATE, DATA_DELETE_TASK,\
    DATA_DELETE_TEMPLATE, DATA_GET_TASK, DATA_GET_TEMPLATE
from aops_manager.conf import configuration
from aops_manager.function.verify.deploy import GenerateTaskSchema, DeleteTaskSchema,\
    GetTaskSchema, ExecuteTaskSchema, ImportTemplateSchema, DeleteTemplateSchema, GetTemplateSchema
from aops_manager.deploy_manager.run_task import TaskRunner
from aops_manager.account_manager.key import HostKey
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder


class GenerateTask(Resource):
    """
    Interface for generate Task
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Generate task

        Args:
            task_name(str): name of task
            description(str): description of the task
            template_name(list); template name list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, GenerateTaskSchema, access_token)
        if verify_res != SUCCEED:
            response = StatusCode.make_response(verify_res)
            return jsonify(response)

        # generate task id
        task_id = str(uuid.uuid1()).replace('-', '')
        args['task_id'] = task_id
        args.pop('template_name')

        # make database center url
        database_url = make_datacenter_url(DATA_ADD_TASK)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)
        if response['code'] == SUCCEED:
            response['task_id'] = task_id

        return jsonify(response)


class DeleteTask(Resource):
    """
    Interface for delete Task
    Restful API: delete
    """
    @staticmethod
    def delete():
        """
        Delete task

        Args:
            task_list(list): task name list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_TASK)
        verify_res = MyResponse.verify_all(
            args, DeleteTaskSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'delete', database_url, args)

        return jsonify(response)


class GetTask(Resource):
    """
    Interface for get Task
    Restful API: get
    """
    @staticmethod
    def get():
        """
        Get task

        Args:
            task_list(list): task name list
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_TASK)
        verify_res = MyResponse.verify_all(
            args, GetTaskSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'get', database_url, args)

        return jsonify(response)


class ExecuteTask(Resource):
    """
    Interface for execute Task
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Execute task

        Args:
            task_list(list): task id list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, ExecuteTaskSchema, access_token)
        if verify_res != SUCCEED:
            response = StatusCode.make_response(verify_res)
            return jsonify(response)
        inventory = InventoryBuilder()
        LOGGER.debug(args)
        task_list = args.get('task_list')
        LOGGER.info("Start run task %s", task_list)

        succeed_list = []
        fail_list = []

        database_url = make_datacenter_url(DATA_GET_TASK)
        pyload = {
                "task_list": task_list,
                "username": "admin"
            }

        response = MyResponse.get_result(verify_res, 'get', database_url, pyload)
        if response['code'] != SUCCEED:
            return jsonify(response)
        for task_info in response['task_infos']:
            task_id = task_info['task_id']
            if not task_info.get('host_list'):
                return StatusCode.make_response(PARAM_ERROR)
            for host in task_info['host_list']:
                print(configuration.manager.get('HOST_VARS'), host['host_name'])
                inventory.move_host_vars_to_inventory(configuration.manager.get('HOST_VARS'),
                                                      host['host_name'])
            res = TaskRunner.run_task(task_id, HostKey.key)
            if res:
                succeed_list.append(task_id)
                LOGGER.info("task %s execute succeed", task_id)
                inventory.remove_host_vars_in_inventory()
                continue
            else:
                fail_list.append(task_id)
                LOGGER.warning("task %s execute fail", task_id)

        response = StatusCode.make_response(SUCCEED)
        response['succeed_list'] = succeed_list
        response['fail_list'] = fail_list

        return jsonify(response)


class ImportTemplate(Resource):
    """
    Interface for import template
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Add template

        Args:
            template_name(str): template name
            template_content(dict): content
            description(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_ADD_TEMPLATE)
        verify_res = MyResponse.verify_all(
            args, ImportTemplateSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class GetTemplate(Resource):
    """
    Interface for get template info.
    Restful API: GET
    """
    @staticmethod
    def get():
        """
        Get template info

        Args:
            template_list(list): template name list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_TEMPLATE)
        verify_res = MyResponse.verify_all(
            args, GetTemplateSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'get', database_url, args)

        return jsonify(response)


class DeleteTemplate(Resource):
    """
    Interface for delete template.
    Restful API: DELETE
    """
    @staticmethod
    def delete():
        """
        Delete template

        Args:
            template_list(list): template name list

        Returns:
            dict: response body
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_TEMPLATE)
        verify_res = MyResponse.verify_all(
            args, DeleteTemplateSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'delete', database_url, args)

        return jsonify(response)
