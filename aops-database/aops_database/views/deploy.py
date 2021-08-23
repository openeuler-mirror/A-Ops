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
from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_database.proxy.deploy import DeployDatabase
from aops_database.function.helper import operate
from aops_utils.restful.status import make_response


class AddTask(Resource):
    """
    Interface for add Task
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Add task

        Args:
            task_name(str)
            description(str)
            task_id(str)
            username(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        action = 'add_task'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

        return jsonify(response)


class DeleteTask(Resource):
    """
    Interface for delete Task
    Restful API: DELETE
    """
    @staticmethod
    def delete():
        """
        Delete task

        Args:
            task_list(list): task id list
            username(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        action = 'delete_task'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

        return jsonify(response)


class GetTask(Resource):
    """
    Interface for get Task
    Restful API: GET
    """
    @staticmethod
    def get():
        """
        Get task

        Args:
            task_list(list): task id list
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        args = request.get_json()
        action = 'get_task'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

        return jsonify(response)


class AddTemplate(Resource):
    """
    Interface for add template
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
            username(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        action = 'add_template'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

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
            template_list(list): template id list
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        args = request.get_json()
        action = 'get_template'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

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
        action = 'delete_template'
        deploy_proxy = DeployDatabase()
        response = make_response(operate(deploy_proxy, args, action))

        return jsonify(response)
