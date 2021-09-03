#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/23 20:20
docs: view.py
description: Check scheduler processing
Class: ImportCheckRule, GetCheckRule, DeleteCheckRule, GetCheckResult
"""

import json
from flask import request, jsonify
from flask_restful import Resource
from adoctor_check_scheduler.common.constant import CheckTopic
from adoctor_check_scheduler.common.check_verify import ImportRuleSchema, \
    GetCheckRuleSchema, DeleteCheckRuleSchema, \
    GetCheckResultSchema, GetCheckResultCountSchema
from adoctor_check_scheduler.common.config import scheduler_check_config
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_datacenter_url
from aops_utils.conf.constant import DATA_ADD_CHECK_RULE, DATA_DELETE_CHECK_RULE, \
    DATA_GET_CHECK_RULE, DATA_GET_CHECK_RULE_COUNT, \
    DATA_GET_CHECK_RESULT, DATA_GET_CHECK_RESULT_COUNT
from aops_utils.restful.status import SUCCEED, PARTIAL_SUCCEED, PARAM_ERROR
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER


class ImportCheckRule(Resource):
    """
    Process /check/rule/import
    """

    @staticmethod
    def _pre_check(check_items):
        """
        Check the check_item configuration in advance.
        Args:
            check_items (list): check_items config
        """
        check_item_name = set()
        for check_item in check_items:
            check_item_name.add(check_item.get("check_item"))
        return len(check_item_name) == len(check_items)

    @staticmethod
    def post():
        """
        Import check rule into system
        Input :
            {
                "check_items": [
                    {
                        "check_item": "item1",
                        "data_list": [
                            {
                                "name": "data_item1",
                                "label": {
                                    "mode": "irq"
                                }
                            }
                        ],
                        "condition": "",
                        "plugin":"",
                        "description": "",
                    }
                ]
            }

        Return:
            {
                "code": "",
                "msg": ""
            }

        """

        args = json.loads(request.get_data())
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, ImportRuleSchema, access_token)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})

        if not ImportCheckRule._pre_check(args.get("check_items")):
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Duplicate check items."})

        # Forward to executor
        try:
            producer = BaseProducer(scheduler_check_config)
            producer.send_msg(CheckTopic.import_check_rule_topic, args)
        except ProducerInitError as exp:
            LOGGER.error("Produce import check rule msg failed. %s", exp)
            response = {"code": PARTIAL_SUCCEED,
                        "msg": "import check rule to check executor failed."}
            return jsonify(response)

        # Forward to database
        database_url = make_datacenter_url(DATA_ADD_CHECK_RULE)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class GetCheckRule(Resource):
    """
    Process /check/rule/get
    """

    @staticmethod
    def post():
        """
        Get check rule info from database
        Input :
            {
                "check_items": [],
                "page": 1,
                "per_page": 50
            }

        Return:
            {
                "code": "",
                "msg": "",
                "total_count": 1,
                "total_page": 1,
                "check_items": [
                    {
                        "check_item": "item1",
                        "data_list": ["data1", "data2"],
                        "condition": "",
                        "description": "",
                        "plugin": ""
                    }
                ]
            }
        """
        # Forward to database
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, GetCheckRuleSchema, access_token)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})
        database_url = make_datacenter_url(DATA_GET_CHECK_RULE)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class DeleteCheckRule(Resource):
    """
    Process /check/rule/delete
    """

    @staticmethod
    def delete():
        """
        Delete check rule
        Input :
            {
                "check_items": ["cpu_usage_overflow"]
            }


        Return:
            {
                "code": "",
                "msg": ""
            }
        """
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, DeleteCheckRuleSchema, access_token)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})

        # Forward to executor
        try:
            producer = BaseProducer(scheduler_check_config)
            producer.send_msg(CheckTopic.delete_check_rule_topic, args)
        except ProducerInitError as exp:
            LOGGER.error("Produce delete check rule msg failed. %s", exp)
            response = {"code": PARTIAL_SUCCEED,
                        "msg": "delete check rule to check executor failed."}
            return jsonify(response)

        # Forward to database
        database_url = make_datacenter_url(DATA_DELETE_CHECK_RULE)
        response = MyResponse.get_result(
            verify_res, 'delete', database_url, args)

        return jsonify(response)


class GetCheckResult(Resource):
    """
        Process /check/result/get
    """

    @staticmethod
    def post():
        """
        Get check result
        Input :
            {
                "time_range": [11, 22],
                "check_items": ["xxx"],
                "host_list": ["host1"],
                "page": 1,
                "per_page": 50
            }

        Return:
            {
                "code": "",
                "msg": "",
                "total_count": 1,
                "total_page": 1,
                "check_result": [
                    {
                        "host_id": "host1",
                        "data_list": ['data1', 'data2'],
                        "start": 11,
                        "end": 25,
                        "check_item": "xxx",
                        "condition": "",
                        "value": ""
                    }
                ]
            }
        """
        # Forward to database
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, GetCheckResultSchema, access_token)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})

        database_url = make_datacenter_url(DATA_GET_CHECK_RESULT)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)
        return jsonify(response)


class GetCheckRuleCount(Resource):
    """
        Process /check/rule/count
    """

    @staticmethod
    def post():
        """
        Get check rule count
        Input :
            {
            }

        Return:
            {
                "code": "",
                "msg": "",
                "rule_count": 1
            }

        """
        # Forward to database
        args = request.get_json()
        if args != {}:
            LOGGER.error("Invalid args %s", args)
            return jsonify({"code": PARAM_ERROR, "msg": "Verify msg param failed"})
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_token(access_token, args)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})

        database_url = make_datacenter_url(DATA_GET_CHECK_RULE_COUNT)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)


class GetCheckResultCount(Resource):
    """
    Process
    """

    @staticmethod
    def post():
        """
        Get check result count
        Input :
            {
                "host_list": [],
                "page": 1,
                "per_page": 50
            }

        Return:
            {
                "code": "",
                "msg": "",
                "total_count": 1,
                "total_page": 1,
                "results": [
                    {
                        "host_id": "id1",
                        "count": 2
                    }
                ]
            }

        """
        # Forward to database
        args = request.get_json()
        access_token = request.headers.get('access_token')
        verify_res = MyResponse.verify_all(
            args, GetCheckResultCountSchema, access_token)
        if verify_res != SUCCEED:
            LOGGER.error("verify args failed %s", verify_res)
            return jsonify({"code": verify_res, "msg": "Verify msg param failed"})

        database_url = make_datacenter_url(DATA_GET_CHECK_RESULT_COUNT)
        response = MyResponse.get_result(
            verify_res, 'post', database_url, args)

        return jsonify(response)
