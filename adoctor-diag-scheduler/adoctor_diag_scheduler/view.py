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
Description: Diagnose processing
Class: DiagTask
"""

from flask import request, jsonify
from flask_restful import Resource
from kafka.errors import KafkaError

from aops_utils.restful.helper import make_datacenter_url
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import StatusCode, SUCCEED, SERVER_ERROR
from aops_utils.log.log import LOGGER
from aops_utils.conf.constant import DATA_ADD_DIAG_TREE, DATA_GET_DIAG_TREE, \
    DATA_DELETE_DIAG_REPORT, DATA_DELETE_DIAG_TREE, DATA_GET_DIAG_TASK, DATA_GET_DIAG_PROCESS, \
    DATA_GET_DIAG_REPORT, DATA_GET_DIAG_REPORT_LIST
from adoctor_diag_scheduler.function.producer import Producer
from adoctor_diag_scheduler.function.verify import AddTreeSchema, ExecuteDiagSchema,\
    GetTreeSchema, DeleteTreeSchema, DeleteReportSchema, GetTaskSchema, GetProgressSchema, \
    GetReportListSchema, GetReportSchema
from adoctor_diag_scheduler.conf import diag_configuration


class AddDiagTree(Resource):
    """
    Restful interface for import diagnose tree.
    """
    @staticmethod
    def post():
        """
        Import diagnose tree into database

        Args:
            trees (list): list of trees' info dict
                e.g. [{
                        "tree_name": "tree1",
                        "tree_content": {},
                        "description": ""
                    }]

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_ADD_DIAG_TREE)

        verify_res = MyResponse.verify_all(
            args, AddTreeSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class GetDiagTree(Resource):
    """
    Restful interface for export diagnose trees.
    """
    @staticmethod
    def post():
        """
        Get diag trees' info from database

        Args:
            tree_list (list): list of trees' name

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_DIAG_TREE)

        verify_res = MyResponse.verify_all(
            args, GetTreeSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class DelDiagTree(Resource):
    """
    Restful interface for delete diagnose trees.
    """
    @staticmethod
    def delete():
        """
        Delete diag trees from database

        Args:
            tree_list (list): list of trees' name

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_DIAG_TREE)

        verify_res = MyResponse.verify_all(
            args, DeleteTreeSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'DELETE', database_url, args)

        return jsonify(response)


class ExecuteDiag(Resource):
    """
    Restful interface for execute diagnose.
    """
    @staticmethod
    def post():
        """
        Do diagnose of hosts based on specific trees and time range

        Args:
            host_list (list): list of hosts
            time_range (list): time range of diagnose
            tree_list (list): list of trees

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')

        verify_res = MyResponse.verify_all(
            args, ExecuteDiagSchema, access_token)
        if verify_res != SUCCEED:
            response = StatusCode.make_response(verify_res)
            return jsonify(response)

        try:
            producer = Producer(diag_configuration)
            task_id, jobs_num = producer.create_msgs(args)
            LOGGER.info("%d kafka messages created." % jobs_num)
            response = StatusCode.make_response(SUCCEED)
            response["task_id"] = task_id
            response["expected_report_num"] = jobs_num

        except (KeyError, KafkaError) as err:
            LOGGER.error(err)
            response = StatusCode.make_response(SERVER_ERROR)
            response["task_id"] = None
            response["expected_report_num"] = 0
        return jsonify(response)


class GetDiagTask(Resource):
    """
    Restful interface for get diagnose tasks based on status.
    """
    @staticmethod
    def post():
        """
        Get diagnose tasks from database

        Args:
            status (str): status of diagnose task, for instance, finished

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_DIAG_TASK)

        verify_res = MyResponse.verify_all(
            args, GetTaskSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class Progress(Resource):
    """
    Restful interface for get diagnose progress.
    """
    @staticmethod
    def post():
        """
        Get progress of diagnose
        Args:
            task_list (list): list of tasks id

        Returns:
            dict: response body
        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_DIAG_PROCESS)

        verify_res = MyResponse.verify_all(
            args, GetProgressSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class GetDiagReport(Resource):
    """
    Restful interface for get diagnose report.
    """
    @staticmethod
    def post():
        """
        Get diagnose report from database

        Args:
            report_list (list): list of reports id

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_DIAG_REPORT)

        verify_res = MyResponse.verify_all(
            args, GetReportSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class GetDiagReportList(Resource):
    """
    Restful interface for get diagnose report's list.
    """
    @staticmethod
    def post():
        """
        Get diagnose report from database

        Args:
            time_range (list): time range of reports
            host_list (list): list of hosts
            tree_list (list): list of trees
            page (int): current page in front (optional)
            per_page (int): reports number of each page (optional)

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_GET_DIAG_REPORT_LIST)

        verify_res = MyResponse.verify_all(
            args, GetReportListSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'POST', database_url, args)

        return jsonify(response)


class DelDiagReport(Resource):
    """
    Restful interface for delete diagnose report.
    """
    @staticmethod
    def delete():
        """
        Delete diagnose report

        Args:
            tree_list (list): list of trees' ame

        Returns:
            dict: response body

        """
        args = request.get_json()
        LOGGER.debug(args)
        access_token = request.headers.get('access_token')
        database_url = make_datacenter_url(DATA_DELETE_DIAG_REPORT)

        verify_res = MyResponse.verify_all(
            args, DeleteReportSchema, access_token)
        response = MyResponse.get_result(
            verify_res, 'DELETE', database_url, args)

        return jsonify(response)
