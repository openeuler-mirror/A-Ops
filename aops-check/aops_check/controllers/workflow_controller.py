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
"""
Time:
Author:
Description:
"""
import uuid
from typing import Dict, Tuple
from flask import jsonify, request

from aops_utils.database.helper import operate
from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import SUCCEED, WORKFLOW_ASSIGN_MODEL_FAIL, DATABASE_CONNECT_ERROR
from aops_utils.log.log import LOGGER

from aops_check.conf import configuration
from aops_check.database import SESSION
from aops_check.database.dao.workflow_dao import WorkflowDao
from aops_check.core.rule.workflow import Workflow
from aops_check.utils.schema.workflow import CreateWorkflowSchema, QueryWorkflowSchema, \
    QueryWorkflowListSchema, DeleteWorkflowSchema, UpdateWorkflowSchema, IfHostInWorkflowSchema, \
    ExecuteWorkflowSchema, StopWorkflowSchema
from aops_check.errors.workflow_error import WorkflowModelAssignError
from aops_check.core.check.check_scheduler.check_scheduler import check_scheduler


class CreateWorkflow(BaseResponse):
    """
    Create workflow interface, it's a post request.
    """

    @staticmethod
    def _handle(args: dict) -> Tuple[int, Dict[str, str]]:
        """
        Args:
            args: dict of workflow info, e.g.
                {
                    "username": "admin",
                    "workflow_name": "workflow1",
                    "description": "a long description",
                    "app_name": "app1",
                    "app_id": "asd",
                    "input": {
                        "domain": "host_group_1",
                        "hosts": ["host_id1", "host_id2"]
                    },
                    "step": 5,  // optional
                    "period": 15,  // optional
                    "alert": {}  // optional
                }
        """
        result = {}

        access_token = request.headers.get('access_token')
        try:
            host_infos, detail = Workflow.assign_model(args["username"], access_token, args["app_id"],
                                            args["input"]["hosts"], "app")
        except (WorkflowModelAssignError, KeyError) as error:
            LOGGER.debug(error)
            return WORKFLOW_ASSIGN_MODEL_FAIL, result

        model_info = Workflow.get_model_info(detail)

        args['step'] = args.get('step', 5)
        args["period"] = args.get("period", 15)
        args["alert"] = args.get("alert", {})
        args["status"] = "hold"
        workflow_id = str(uuid.uuid1()).replace('-', '')
        args['workflow_id'] = workflow_id
        args["detail"] = detail
        args["model_info"] = model_info
        # change host id list to host info dict
        args["input"]["hosts"] = host_infos

        status = operate(WorkflowDao(configuration), args, 'insert_workflow', SESSION)
        if status != SUCCEED:
            return status, result

        result['workflow_id'] = workflow_id
        return status, result

    def post(self):
        """
        It's post request, step:
            1.verify token;
            2.verify args;
            3.add default args
            4.insert into database
        """
        return jsonify(self.handle_request(CreateWorkflowSchema, self))


class QueryWorkflow(BaseResponse):
    """
    Query workflow interface, it's a get request.
    """

    def get(self):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.get workflow from database
        """
        return jsonify(self.handle_request_db(QueryWorkflowSchema,
                                              WorkflowDao(configuration),
                                              "get_workflow", SESSION))


class QueryWorkflowList(BaseResponse):
    """
    Query workflow interface, it's a post request.
    """

    def post(self):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.get workflow list from database
        """
        return jsonify(self.handle_request_db(QueryWorkflowListSchema,
                                              WorkflowDao(configuration),
                                              "get_workflow_list", SESSION))


class ExecuteWorkflow(BaseResponse):
    """
    Execute workflow interface, it's a post request
    """
    @staticmethod
    def _handle(args: dict) -> int:
        """
        Args:
            args: dict of workflow id, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }
        """
        workflow_id = args["workflow_id"]
        username = args["username"]
        workflow_proxy = WorkflowDao(configuration)
        if not workflow_proxy.connect(SESSION):
            return DATABASE_CONNECT_ERROR

        status_code, result = workflow_proxy.get_workflow(args)

        if status_code != SUCCEED:
            return status_code

        workflow_info = result["result"]
        if workflow_info["status"] != "hold":
            LOGGER.info("Workflow '%s' cannot execute with status '%s'." %
                        (workflow_id, workflow_info["status"]))
            return SUCCEED

        workflow_proxy.update_workflow_status(workflow_id, "running")
        check_scheduler.start_workflow(workflow_id, username, workflow_info["step"])
        return SUCCEED

    def post(self):
        """
        It's a post request, step
            1.verify token
            2.verify args
            3.check workflow exists or not, check status and change to running
            4.execute workflow
        """
        return jsonify(self.handle_request(ExecuteWorkflowSchema, self))


class StopWorkflow(BaseResponse):
    """
    Stop workflow interface, it's a post request
    """
    @staticmethod
    def _handle(args: dict) -> int:
        """
        Args:
            args: dict of workflow id, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }
        """
        workflow_id = args["workflow_id"]
        workflow_proxy = WorkflowDao(configuration)
        if not workflow_proxy.connect(SESSION):
            return DATABASE_CONNECT_ERROR

        status_code, result = workflow_proxy.get_workflow(args)

        if status_code != SUCCEED:
            return status_code

        workflow_info = result["result"]
        if workflow_info["status"] != "running":
            LOGGER.info("Workflow '%s' cannot stop with status '%s'." %
                        (workflow_id, workflow_info["status"]))
            return SUCCEED

        workflow_proxy.update_workflow_status(workflow_id, "hold")
        check_scheduler.stop_workflow(workflow_id)
        return SUCCEED

    def post(self):
        """
        It's a post request, step
            1.verify token
            2.verify args
            3.check workflow exists or not, check status and change to hold
            4.stop workflow
        """
        return jsonify(self.handle_request(StopWorkflowSchema, self))


class DeleteWorkflow(BaseResponse):
    """
    Delete workflow interface, it's a delete request.
    """

    def delete(self):
        """
        It's delete request, step:
            1.verify token
            2.verify args
            3.check if workflow running
            4.delete workflow from database
        """
        return jsonify(self.handle_request_db(DeleteWorkflowSchema,
                                              WorkflowDao(configuration),
                                              "delete_workflow", SESSION))


class UpdateWorkflow(BaseResponse):
    """
    Update workflow interface, it's a post request.
    """
    @staticmethod
    def _handle(args: dict):
        """
        create new model info based on the detail info given by request
        Args:
            args:  e.g.
                {
                    "username": "admin",
                    "workflow_id": "id1",
                    "workflow_name": "new_name",
                    "description": "new description",
                    "step": 10,
                    "period": 10,
                    "alert": {},
                    "detail": {...}
                }

        Returns:
            dict: a dict with detail info and model info
        """
        model_info = Workflow.get_model_info(args["detail"])
        args["model_info"] = model_info

        status = operate(WorkflowDao(configuration), args, 'update_workflow', SESSION)
        return status

    def post(self):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.update workflow in database
        """
        return jsonify(self.handle_request(UpdateWorkflowSchema, self))


class IfHostInWorkflow(BaseResponse):
    """
    if hosts exist workflow
    """

    def post(self):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.check if host in a workflow
        """
        return jsonify(self.handle_request_db(IfHostInWorkflowSchema,
                                              WorkflowDao(configuration),
                                              "if_host_in_workflow", SESSION))
