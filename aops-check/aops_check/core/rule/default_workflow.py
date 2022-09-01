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
from typing import Dict, Tuple
import uuid
from importlib import import_module

from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.kafka.producer import BaseProducer

from aops_check.core.experiment.app.network_diagnose import NetworkDiagnoseApp
from aops_check.core.rule.model_assign import ModelAssign
from aops_check.database.dao.data_dao import DataDao
from aops_check.errors.workflow_error import WorkflowModelAssignError
from aops_check.conf import configuration
from aops_check.conf.constant import ALGO_LIST
from aops_utils.restful.status import SUCCEED, DATABASE_CONNECT_ERROR, DATABASE_QUERY_ERROR,\
    TASK_EXECUTION_FAIL, PARTIAL_SUCCEED
from aops_check.core.experiment.app import App
from aops_utils.log.log import LOGGER


class DefaultWorkflow:

    def __init__(self, hosts: list, app=NetworkDiagnoseApp):
        if not issubclass(app, App):
            raise TypeError()
        self.__app = app()
        self.__hosts = DefaultWorkflow._generate_hosts(hosts)
        self.__detail_info = self.__generate_workflow_detail(hosts)
        self.__model_info = self.__generate_model_info()

    def __generate_workflow_detail(self, hosts) -> dict:
        hosts = [host["ip"] for host in hosts]
        workflow_detail = dict()
        step_detail = self.__app.info["detail"]
        try:
            if "singlecheck" in step_detail:
                failed_list, workflow_detail["singlecheck"] = DefaultWorkflow.__assign_single_item_model(hosts,
                                                                                                         step_detail["singlecheck"])
                if failed_list:
                    LOGGER.debug(
                        "Query metric list of host '%s' failed when assign " % failed_list)
            if "multicheck" in step_detail:
                workflow_detail["multicheck"] = DefaultWorkflow.__assign_multi_item_model(
                    hosts)
            if "diag" in step_detail:
                workflow_detail["diag"] = ModelAssign.assign_cluster_diag_model()

        except ValueError as error:
            LOGGER.error("Generate workflow detail failed.")
            LOGGER.error(error)
            raise WorkflowModelAssignError(str(error))
        return workflow_detail

    def __generate_model_info(self) -> dict:
        model_set = set()
        if "singlecheck" in self.__detail_info:
            single_check_detail = self.__detail_info["singlecheck"]
            for metric_info in single_check_detail.values():
                model_set.update(metric_info.values())

        if "multicheck" in self.__detail_info:
            multi_check_detail = self.__detail_info["multicheck"]
            model_set.update(multi_check_detail.values())

        if "diag" in self.__detail_info:
            model_set.add(self.__detail_info["diag"])
        return DefaultWorkflow.__analysis_model_info(list(model_set))

    @staticmethod
    def __analysis_model_info(model_list: list) -> dict:
        model_info = dict()
        for algo in ALGO_LIST:
            module_path, class_name = algo["algo_module"].rsplit('.', 1)
            algo_class = getattr(import_module('.', module_path), class_name)
            algo_id = str(uuid.uuid1()).replace('-', '')

            for model_detail in algo["models"]:
                if model_detail['model_id'] not in model_list:
                    continue
                model_info[model_detail['model_id']] = {"model_name": model_detail['model_name'], "algo_id": algo_id,
                                                        "algo_name": algo_class().info.get('algo_name')}
        return model_info

    @staticmethod
    def _generate_hosts(hosts):
        hosts = list()
        for host_ip in hosts:
            hosts.append(
                {"host_id": host_ip["ip"], "public_ip": host_ip["ip"], "instance_port": host_ip["port"]})
        return hosts

    def _get_app_execute_result(self, time_range):
        data_dao = DataDao(configuration)
        if not data_dao.connect():
            LOGGER.error("Promethus connection failed.")
            return DATABASE_CONNECT_ERROR, None

        data_status, monitor_data = data_dao.query_data(
            time_range=time_range, host_list=self.__hosts)

        if data_status != SUCCEED and data_status != PARTIAL_SUCCEED:
            LOGGER.error("Promethus data query error.")
            return DATABASE_QUERY_ERROR, None

        network_monitor_data = self.__app.execute(
            model_info=self.__model_info, detail=self.__detail_info, data=monitor_data, default_mode=True)
        if not network_monitor_data:
            LOGGER.debug("No error message.")

        return SUCCEED, network_monitor_data

    @staticmethod
    def _kafka_host_check_msg(network_monitor_data):
        host_check = dict()
        for host_ip, metrics in network_monitor_data.get("host_result", dict()).items():
            if not isinstance(metrics, list):
                continue
            for metric_item in metrics:
                host_check[host_ip] = dict(is_root=metric_item.get("is_root", False),
                                           metric_name=metric_item.get(
                                               "metric_name"),
                                           metric_label=metric_item.get("metric_label"))
        return host_check

    def _send_kafka(self, network_monitor_data):
        workflow_msg = {
            "alert_name": network_monitor_data["alert_name"],
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

    def execute(self, time_range: list) -> int:
        """
        Defaultworkflow control
        Args:
            time_range: ["1660471200"]
        Returns:
            int
        """
        app_execute_status, network_monitor_data = self._get_app_execute_result(
            time_range)
        if app_execute_status != SUCCEED or not network_monitor_data:
            return app_execute_status

        send_result = self._send_kafka(network_monitor_data)
        if send_result != SUCCEED:
            LOGGER.error("Description failed to send a kafka message.")
        else:
            LOGGER.debug(
                "Insert workflow execute result into kafka successful.")
        return send_result

    @staticmethod
    def __assign_single_item_model(hosts_info: list, config: dict = None) -> Tuple[list, Dict[str, Dict[str, str]]]:
        """
        assign single item check model
        Args:
            hosts_info: host id, ip and scene, e.g.
                ["127.0.0.1","192.168.1.1"]
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

        for host_ip in hosts_info:
            # query host's metric list
            status_code, metric_label_list = data_proxy.query_metric_list_of_host(
                host_ip)
            if status_code != SUCCEED:
                failed_list.append(host_ip)
                continue

            metric_list = DefaultWorkflow.__get_metric_names(metric_label_list)
            host_algo[host_ip] = ModelAssign.assign_kpi_model_by_name(
                metric_list, config)
        return failed_list, host_algo

    @staticmethod
    def __get_metric_names(metric_label_list: list) -> list:
        """
        split metric name and label, get metric name list
        Args:
            metric_label_list: metric name and label string list

        Returns:
            list: list of metric name
        """
        metric_set = set()
        for metric_label in metric_label_list:
            index = metric_label.find('{')
            metric_name = metric_label[:index]
            metric_set.add(metric_name)

        return list(metric_set)

    @staticmethod
    def __assign_multi_item_model(hosts_info: list) -> Dict[str, str]:
        """
        assign multiple item check model
        Args:
            hosts_info: host ip e.g.
                ["127.0.0.1","192.168.1.1"]
        Returns:
            dict
        Raises:
            ValueError
        """
        host_algo = {host_ip: "StatisticalCheck-1" for host_ip in hosts_info}
        return host_algo
