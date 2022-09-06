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
import time
from typing import Dict, Tuple

import sqlalchemy
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.kafka.producer import BaseProducer
from aops_utils.restful.status import SUCCEED, DATABASE_INSERT_ERROR, TASK_EXECUTION_FAIL,\
    DATABASE_QUERY_ERROR, DATABASE_CONNECT_ERROR
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import MyResponse
from aops_utils.conf.constant import URL_FORMAT, QUERY_HOST_DETAIL
from aops_utils.database.helper import operate

from aops_check.database import SESSION
from aops_check.conf import configuration
from aops_check.errors.workflow_error import WorkflowExecuteError, WorkflowModelAssignError
from aops_check.database.dao.data_dao import DataDao
from aops_check.database.dao.app_dao import AppDao
from aops_check.database.dao.model_dao import ModelDao
from aops_check.core.rule.model_assign import ModelAssign
from aops_check.database.dao.workflow_dao import WorkflowDao
from aops_check.database.dao.result_dao import ResultDao
from aops_check.core.experiment.app.network_diagnose import NetworkDiagnoseApp


class Workflow:
    """
    Workflow manager
    """

    def __init__(self, username, workflow_id):
        self.__workflow_id = workflow_id
        self.__username = username
        self.__app_id = ""
        self.__hosts = []
        self.__status = "hold"
        self.__detail = {}
        self.__model_info = {}

    @property
    def detail(self):
        return self.__detail

    def _insert_domain(self, result_dao, alert_id, domain, insert_time, network_monitor_data, workflow_name):
        insert_status = result_dao.insert_domain(data=dict(alert_id=alert_id, domain=domain,
                                                           alert_name=network_monitor_data["alert_name"],
                                                           time=insert_time, workflow_name=workflow_name,
                                                           workflow_id=self.__workflow_id,
                                                           username=self.__username,
                                                           level=None, confirmed=False
                                                           ))
        if insert_status != SUCCEED:
            LOGGER.debug("Failed to insert domain workflow data.")
            raise WorkflowExecuteError

    @staticmethod
    def _insert_alert_host(result_dao, workflow, alert_id):
        hosts = workflow["input"]["hosts"]
        for host_id, host in hosts.items():
            if result_dao.insert_alert_host(data=dict(host_id=host_id,
                                                      alert_id=alert_id,
                                                      host_ip=host.get(
                                                          "host_ip"),
                                                      host_name=host.get("host_name"))) != SUCCEED:
                LOGGER.debug("Failed to insert alert host workflow data.")
                raise WorkflowExecuteError

    @staticmethod
    def _insert_host_check(result_dao, network_monitor_data, insert_time):
        for host_id, metrics in network_monitor_data.get("host_result", dict()).items():
            if not isinstance(metrics, list):
                continue
            for metric_item in metrics:
                if result_dao.insert_host_check(data=dict(host_id=host_id,
                                                          time=insert_time,
                                                          is_root=metric_item.get(
                                                              "is_root", False),
                                                          metric_name=metric_item.get(
                                                              "metric_name"),
                                                          metric_label=metric_item.get(
                                                              "metric_label"))) != SUCCEED:
                    LOGGER.debug("Failed to insert host check workflow data.")
                    raise WorkflowExecuteError

    def add_workflow_alert(self, network_monitor_data: dict, workflow: dict, domain: str) -> int:
        result_dao = ResultDao()
        if not result_dao.connect(SESSION):
            LOGGER.error("Connect mysql fail when insert built-in algorithm.")
            raise sqlalchemy.exc.SQLAlchemyError("Connect mysql failed.")
        _time = str(int(time.time()))
        alert_id = _time + "-" + domain
        try:
            self._insert_domain(result_dao, alert_id, domain,
                                _time, network_monitor_data, workflow["workflow_name"])

            self._insert_alert_host(result_dao, workflow, alert_id)

            self._insert_host_check(
                result_dao, network_monitor_data, _time)

            LOGGER.debug("Insert the success, workflow name: %s workflow id: %s" % (
                workflow["workflow_name"], self.__workflow_id))
            return SUCCEED
        except WorkflowExecuteError:
            if result_dao.delete_alert(alert_id=alert_id) != SUCCEED:
                LOGGER.error(
                    "Failed to delete the domain info, alert_id: %s." % alert_id)
            return DATABASE_INSERT_ERROR

    @staticmethod
    def _kafka_alert_host_msg(workflow) -> dict:
        hosts = workflow["input"]["hosts"]
        alert_hosts = dict()
        for host_id, host in hosts.items():
            alert_hosts[host_id] = dict(host_ip=host.get("host_ip"),
                                        host_name=host.get("host_name"))
        return alert_hosts

    @staticmethod
    def _kafka_host_check_msg(network_monitor_data):
        host_check = dict()
        for host_id, metrics in network_monitor_data.get("host_result", dict()).items():
            if not isinstance(metrics, list):
                continue
            for metric_item in metrics:
                host_check[host_id] = dict(is_root=metric_item.get(
                    "is_root", False),
                    metric_name=metric_item.get(
                    "metric_name"),
                    metric_label=metric_item.get(
                    "metric_label"))
        return host_check

    def _send_kafka(self, network_monitor_data, workflow, domain):
        workflow_msg = {
            "domain": domain,
            "alert_name": network_monitor_data["alert_name"],
            "time": str(int(time.time())),
            "workflow_name": workflow["workflow_name"],
            "workflow_id": self.__workflow_id,
            "username": self.__username,
            "level": None,
            "confirmed": False,
            "alert_host": self._kafka_alert_host_msg(workflow),
            "host_check": self._kafka_host_check_msg(network_monitor_data)
        }
        try:
            producer = BaseProducer(configuration)
            LOGGER.debug("Send workflow msg %s" % workflow_msg)
            producer.send_msg(configuration.consumer.get(
                'RESULT_NAME'), workflow_msg)
            return SUCCEED
        except ProducerInitError as error:
            LOGGER.error("Produce workflow msg failed. %s" % error)
            return TASK_EXECUTION_FAIL

    def _get_workflow(self):
        workflow_dao = WorkflowDao(configuration)
        if not workflow_dao.connect(SESSION):
            LOGGER.error("Connect mysql fail when insert built-in algorithm.")
            return DATABASE_CONNECT_ERROR

        status_code, workflow = workflow_dao.get_workflow(
            data=dict(username=self.__username, workflow_id=self.__workflow_id))

        if status_code != SUCCEED:
            return DATABASE_QUERY_ERROR

        workflow = workflow.get("result", dict())

        hosts = []
        try:
            domain = workflow["input"]["domain"]
            for host_id, host in workflow["input"]["hosts"].items():
                hosts.append(
                    dict(host_id=host_id, public_ip=host.get('host_ip')))
        except KeyError:
            LOGGER.error("No valid 'hosts' are queried in workflow")
            return DATABASE_QUERY_ERROR
        return dict(workflow=workflow, hosts=hosts, domain=domain)
    
    def _get_app_execute_result(self, time_range, hosts, workflow):
        data_dao = DataDao(configuration)
        if not data_dao.connect():
            LOGGER.error("Promethus connection failed.")
            return DATABASE_CONNECT_ERROR

        data_status, monitor_data = data_dao.query_data(
            time_range=time_range, host_list=hosts)

        if data_status != SUCCEED:
            LOGGER.error("Data query error")
            return DATABASE_QUERY_ERROR

        LOGGER.debug("Finish querying workflow '%s' data and original data, start executing app."
                     % self.__workflow_id)

        app = NetworkDiagnoseApp()
        network_monitor_data = app.execute(model_info=workflow.get(
            "model_info"), detail=workflow.get("detail"), data=monitor_data)
        if not network_monitor_data:
            LOGGER.debug("No error message,workflow id: %s." % self.__workflow_id)
            return SUCCEED

        return network_monitor_data

    def execute(self, time_range: list, kafka=False, storage=True) -> int:
        """
        Workflow control
        Args:
            time_range: ["1660471200"]
            kafka: True
            storage: True
        Returns:
            int
        """
        workflow = self._get_workflow()
        if isinstance(workflow,int):
            return workflow

        network_monitor_data = self._get_app_execute_result(time_range, workflow["hosts"], workflow["workflow"])

        if isinstance(network_monitor_data,int):
            return network_monitor_data

        storage_status, kafka_status = DATABASE_INSERT_ERROR, DATABASE_INSERT_ERROR
        if storage:
            try:
                storage_status = self.add_workflow_alert(
                    network_monitor_data, workflow["workflow"], workflow["domain"])
                LOGGER.debug("Insert workflow '%s' execute result into database successful."
                             % self.__workflow_id)
            except sqlalchemy.exc.SQLAlchemyError:
                storage_status = DATABASE_CONNECT_ERROR
        if kafka:
            kafka_status = self._send_kafka(
                network_monitor_data, workflow["workflow"], workflow["domain"])
            LOGGER.debug(
                "Insert workflow '%s' execute result into kafka successful." % self.__workflow_id)

        return storage_status == SUCCEED or kafka_status == SUCCEED

    @staticmethod
    def assign_model(username: str, token: str, app_id: str, host_list: list,
                     assign_logic: str, steps: list = None, workflow_id: str = "") -> Tuple[dict, dict]:
        """
        assign model to workflow, for configurable mode
        Args:
            username: username
            token: request token in header
            app_id: app id
            host_list: host id list
            assign_logic: the logic to assign model
            steps: the step of workflow to assign model
            workflow_id: workflow id

        Returns:
            tuple [dict, dict]:
                1. host_infos:  e.g.
                    {"host1": {"host_ip": "127.0.0.1", "scene": "big_data", "host_name": "host1"}}
                2. assign result. e.g.
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
        return hosts_info, workflow_detail

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
            raise WorkflowModelAssignError("Parse app info to get steps failed: %s"
                                           % error, workflow_id)

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
            dict: e.g. {"host1": {"host_ip": "127.0.0.1", "scene": "big_data", "host_name": "host1"}}
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
            result[host_info["host_id"]] = {"host_ip": host_info["public_ip"],
                                            "scene": host_info["scene"],
                                            "host_name": host_info["host_name"]}
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
                {"host1": {"host_ip": "127.0.0.1", "scene": "big_data", "host_name": "host1"}}
            step_detail: step which need assigned, if value is None, use recommend logic to assign

        Returns:
            dict
        Raises:
            WorkflowModelAssignError
        """
        result = {}
        try:
            if "singlecheck" in step_detail:
                result["singlecheck"] = Workflow.__assign_single_item_model(hosts_info, step_detail["singlecheck"])
            if "multicheck" in step_detail:
                result["multicheck"] = Workflow.__assign_multi_item_model(hosts_info, step_detail["multicheck"])
            if "diag" in step_detail:
                result["diag"] = Workflow.__assign_cluster_diag_model()
        except ValueError as error:
            raise WorkflowModelAssignError(str(error), workflow_id)
        return result

    @staticmethod
    def __assign_single_item_model(hosts_info: dict, config: dict = None) -> Dict[str, Dict[str, str]]:
        """
        assign single item check model
        Args:
            hosts_info: host id, ip and scene, e.g.
                {"host1": {"host_ip": "127.0.0.1", "scene": "big_data", "host_name": "host1"}}
            config: single item check config
        Returns:
            dict
        Raises:
            ValueError
        """
        host_model = {}

        kpi_model = ModelAssign.assign_kpi_model_by_name(config)
        for host_id, value in hosts_info.items():
            host_model[host_id] = kpi_model
        return host_model

    @staticmethod
    def __assign_multi_item_model(hosts_info: dict, config: dict = None) -> Dict[str, str]:
        """
        assign multiple item check model
        Args:
            hosts_info: host id, ip and scene, e.g.
                {"host1": {"host_ip": "127.0.0.1", "scene": "big_data", "host_name": "host1"}}
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
