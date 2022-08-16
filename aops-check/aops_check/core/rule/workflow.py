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
from typing import Dict, Tuple
from aops_utils.restful.status import SUCCEED
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import MyResponse
from aops_utils.conf.constant import URL_FORMAT, QUERY_HOST_DETAIL
from aops_utils.database.helper import operate

from aops_check.database import SESSION
from aops_check.conf import configuration
from aops_check.errors.workflow_error import WorkflowModelAssignError
from aops_check.database.dao.data_dao import DataDao
from aops_check.database.dao.app_dao import AppDao
from aops_check.database.dao.model_dao import ModelDao
from aops_check.core.rule.model_assign import ModelAssign


class Workflow:
    """
    Workflow manager
    """

    def __init__(self, app_id, hosts):
        self.__workflow_id = ""
        self.__app_id = app_id
        self.__hosts = hosts
        self.__status = "hold"
        self.__detail = {}
        self.__model_info = {}

    @property
    def detail(self):
        return self.__detail

    def load(self):
        pass

    def execute(self):
        pass

    def stop(self):
        pass

    @staticmethod
    def assign_model(username: str, token: str, app_id: str, host_list: list,
                      assign_logic: str, steps: list = None, workflow_id: str = "") -> dict:
        """
        assign model to workflow
        Args:
            username: username
            token: request token in header
            app_id: app id
            host_list: host id list
            assign_logic: the logic to assign model
            steps: the step of workflow to assign model
            workflow_id: workflow id

        Returns:
            dict: assign result. e.g.
                {
                    "singlecheck": {
                        "host_id1": {
                            "metric1": "3sigma"
                        }
                    },
                    "multicheck": {
                        "host_id1": "statistic"
                    },
                    "diag": "statistic"
                }
        Raises:
            WorkflowModelRecoError
        """
        support_assign_logic = ["app", "recommend"]
        if assign_logic not in support_assign_logic:
            raise WorkflowModelAssignError("Assign logic '%s' is not supported, "
                                            "should be inside %s" %
                                            (assign_logic, support_assign_logic), workflow_id)

        hosts_info = Workflow.__get_host_info(token, host_list, workflow_id)
        app_detail = Workflow.__get_app_detail(username, app_id, workflow_id)

        if assign_logic == "app":
            workflow_detail = Workflow.__assign_by_app_logic(workflow_id, hosts_info, app_detail)
        else:
            workflow_detail = Workflow.__assign_by_builtin_logic(workflow_id, hosts_info,
                                                                 app_detail, steps)
        return workflow_detail

    @staticmethod
    def __get_app_detail(username: str, app_id: str, workflow_id: str) -> dict:
        """
        get app's step detail and check the step supported or not
        """
        support_steps = {"singlecheck", "multicheck", "diag"}
        app_proxy = AppDao(configuration)
        if not app_proxy.connect():
            raise WorkflowModelAssignError("Connect to elasticsearch failed.", workflow_id)

        status_code, app_info = app_proxy.query_app({"username": username, "app_id": app_id})
        if status_code != SUCCEED:
            raise WorkflowModelAssignError("Query info of app '%s' failed." % app_id, workflow_id)

        try:
            steps = app_info["result"]["detail"].keys()
        except KeyError as error:
            raise WorkflowModelAssignError("Parse app info to get steps failed: %s" % error, workflow_id)

        if steps and steps - support_steps:
            raise WorkflowModelAssignError("The step %s is not supported to assign model."
                                            % list(steps - support_steps), workflow_id)
        return app_info["result"]["detail"]

    @staticmethod
    def __get_host_info(token: str, host_list: list, workflow_id: str):
        """
        send request to manager and reformat host info
        Args:
            token: token of user
            host_list: host id list
            workflow_id: workflow id
        Returns:
            dict: e.g. {"host1": {"public_ip": "127.0.0.1", "scene": "big_data"}}
        """
        manager_ip = configuration.manager.get("IP")  # pylint: disable=E1101
        manager_port = configuration.manager.get("PORT")  # pylint: disable=E1101
        manager_url = URL_FORMAT % (manager_ip, manager_port, QUERY_HOST_DETAIL)
        header = {
            "access_token": token,
            "Content-Type": "application/json; charset=UTF-8"
        }
        pyload = {"host_list": host_list, "basic": True}

        response = MyResponse.get_response('POST', manager_url, pyload, header)
        if response.get('code') != SUCCEED or not response.get("host_infos"):
            raise WorkflowModelAssignError("Query host info of '%s' failed." % host_list, workflow_id)

        result = {}
        for host_info in response["host_infos"]:
            result[host_info["host_id"]] = {"public_ip": host_info["public_ip"],
                                            "scene": host_info["scene"]}
        return result

    @staticmethod
    def __assign_by_app_logic(workflow_id: str, hosts_info: dict, app_detail: dict) -> dict:
        """
        assign model by app logic
        """
        workflow_detail = Workflow.__assign_model(workflow_id, hosts_info, app_detail)
        return workflow_detail

    @staticmethod
    def __assign_by_builtin_logic(workflow_id: str, hosts_info: dict, app_detail: dict,
                                  steps: list) -> dict:
        """
        assign model by built-in recommend logic
        """
        if steps and set(steps) - set(app_detail.keys()):
            raise WorkflowModelAssignError("Step '%s' is not in app." %
                                            list(set(steps) - set(app_detail.keys())), workflow_id)

        if not steps:
            steps = app_detail.keys()
        new_app_detail = {step: None for step in steps}
        result = Workflow.__assign_model(workflow_id, hosts_info, new_app_detail)
        return result

    @staticmethod
    def __assign_model(workflow_id: str, hosts_info: dict, step_detail: dict) -> dict:
        """
        assign model based on given steps
        Args:
            workflow_id: workflow id
            hosts_info: host basic info.  e.g.
                {"host1": {"public_ip": "127.0.0.1", "scene": "big_data"}}
            step_detail: step which need assigned, if value is None, use recommend logic to assign

        Returns:
            dict
        Raises:
            WorkflowModelAssignError
        """
        result = {}
        try:
            if "singlecheck" in step_detail:
                failed_list, result["singlecheck"] = Workflow.__assign_single_item_model(hosts_info,
                                                                                          step_detail["singlecheck"])
                if failed_list:
                    LOGGER.debug("Query metric list of host '%s' failed when assign "
                                 "model of workflow %s." % (failed_list, workflow_id))
            if "multicheck" in step_detail:
                result["multicheck"] = Workflow.__assign_multi_item_model(hosts_info, step_detail["multicheck"])
            if "diag" in step_detail:
                result["diag"] = Workflow.__assign_cluster_diag_model()
        except ValueError as error:
            raise WorkflowModelAssignError(str(error), workflow_id)
        return result

    @staticmethod
    def __assign_single_item_model(hosts_info: dict, config: dict = None) -> Tuple[list, Dict[str, Dict[str, str]]]:
        """
        assign single item check model
        Args:
            hosts_info: host id, ip and scene, e.g.
                {"host1": {"public_ip": "127.0.0.1", "scene": "big_data"}}
            config: single item check config
        Returns:
            list, dict
        Raises:
            ValueError
        """
        data_proxy = DataDao(configuration)
        if not data_proxy.connect():
            raise WorkflowModelAssignError("Connect to prometheus failed.")

        host_algo = {}
        failed_list = []

        for host_id, value in hosts_info.items():
            # query host's metric list
            status_code, metric_list = data_proxy.query_metric_list_of_host(value["public_ip"])
            if status_code != SUCCEED:
                failed_list.append(host_id)
                continue

            host_algo[host_id] = ModelAssign.assign_kpi_model_by_name(metric_list, config)
        return failed_list, host_algo

    @staticmethod
    def __assign_multi_item_model(hosts_info: dict, config: dict = None) -> Dict[str, str]:
        """
        assign multiple item check model
        Args:
            hosts_info: host id, ip and scene, e.g.
                {"host1": {"public_ip": "127.0.0.1", "scene": "big_data"}}
            config: multi item check config
        Returns:
            dict
        Raises:
            ValueError
        """
        host_algo = {}
        for host_id, value in hosts_info.items():
            host_algo[host_id] = ModelAssign.assign_multi_kpi_model(value["scene"], config)
        return host_algo

    @staticmethod
    def __assign_cluster_diag_model() -> str:
        """
        assign cluster diag model
        Args:

        Returns:
            str
        """
        return ModelAssign.assign_cluster_diag_model()

    @staticmethod
    def get_model_info(workflow_detail: dict) -> dict:
        """
        get workflow's model info, which is model and algorithm's relationship
        Args:
            workflow_detail: workflow's detail info.  e.g.
                {
                    "singlecheck": {
                        "host_id1": {
                            "metric1": "3sigma"
                        }
                    },
                    "multicheck": {
                        "host_id1": "statistic"
                    },
                    "diag": "statistic"
                }

        Returns:
            dict: e.g.
                {
                    "model_id1": {
                        "model_name": "model name1",
                        "algo_name": "algo1",
                        "algo_id": "algo_id1"
                    }
                }
        """
        model_set = set()
        if "singlecheck" in workflow_detail:
            single_check_detail = workflow_detail["singlecheck"]
            for metric_info in single_check_detail.values():
                model_set.update(metric_info.values())
        if "multicheck" in workflow_detail:
            multi_check_detail = workflow_detail["multicheck"]
            model_set.update(multi_check_detail.values())
        if "diag" in workflow_detail:
            model_set.add(workflow_detail["diag"])

        data = {"model_list": list(model_set)}
        status, result = operate(ModelDao(), data, "get_model_algo", SESSION)
        return result
