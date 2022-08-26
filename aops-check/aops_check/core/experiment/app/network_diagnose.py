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
from typing import Dict, List, Tuple, Any

from aops_check.core.experiment.algorithm.base_algo import BaseSingleItemAlgorithm
from aops_check.core.experiment.app import App


class NetworkDiagnoseApp(App):
    @property
    def info(self):
        info = {
            "app_id": "network1",
            "app_name": "default_network",
            "version": "1.0",
            "description": "",
            "username": "admin",
            "api": {
                "type": "api",
                "address": "execute"
            },
            "detail": {
                "singlecheck": {
                    "default_model": "NSigma-1",
                    "model_info": {
                        "gala_gopher_disk_wspeed_kB": "Mae-1",
                        "gala_gopher_file_system_Used": "Mae-1",
                        "gala_gopher_tcp_link_retran_packets": "Mae-1",
                        "gala_gopher_tcp_link_srtt": "Ewma-1",
                        "gala_gopher_tcp_link_tmout_count": "Ewma-1",
                        "gala_gopher_block_count_latency_req": "Ewma-1",
                        "gala_gopher_tcp_link_tcp_oom": "Ewma-1",
                        "gala_gopher_block_latency_req_last": "",
                        "gala_gopher_cpu_sched": "",
                        "gala_gopher_block_latency_flush_last": "",
                        "gala_gopher_tcp_link_receive_rsts": "",
                        "scrape_duration_seconds": "",
                        "scrape_samples_post_metric_relabeling": "",
                        "scrape_samples_scraped": "",
                        "scrape_series_added": "",
                        "up": ""
                    }
                },
                "multicheck": {
                    "default_model": "StatisticalCheck-1"
                },
                "diag": {
                    "default_model": "StatisticDiag-1"
                }
            }
        }
        return info

    def do_single_check(self, detail: Dict[str, Dict[str, str]], data: dict) -> Dict[Any, List[Dict[str, str]]]:
        """
        Args:
            detail: it's a map between metric and model. e.g.
                {
                    "host1": {
                        "metric1": "model1",
                        "metric2": "model2"
                    }
                }
            data: input original data. e.g.
                {
                    "host1": {
                        "metric1{label}": [[time1, value1], [time2, value2]],
                        "metric2{label}": [[time1, value1], [time2, value2]],
                        "metric3{label}": [],
                        "metric4{label}": None
                    },
                    "host2": None # no metric
                }

        Returns:
            dict, e.g. {
                    "host1": [{"metric_name": "m1", "metric_label": "l1"}]
                }
        """
        result = {}
        for host_id, metrics in data.items():
            if metrics is None:
                continue
            temp_result = []
            for metric, value in metrics.items():
                index = metric.find('{')
                metric_name = metric[:index]
                metric_label = metric[index:]
                if value is None or len(value) == 0 or \
                        detail.get(host_id) is None or detail[host_id].get(metric_name) is None:
                    continue
                model: BaseSingleItemAlgorithm = self.model.get(
                    detail[host_id][metric_name])
                if len(model.calculate(value)) > 0:
                    temp_result.append(
                        {'metric_name': metric_name, 'metric_label': metric_label})
            if temp_result:
                result[host_id] = temp_result

        return result

    def do_multi_check(self, detail: Dict[str, str], data: Dict[str, List[str]]) -> Dict[Any, List[str]]:
        """
        Args:
            detail: it's a map between metric and model. e.g.
                {
                    "host1": "model1",
                    "host2": "model2"
                }
            data: it's single check result. e.g.
                {
                    "host1": [{"metric_name": "m1", "metric_label": "l1"}]
                }

        Returns:
            dict, e.g. {
                    "host1": [{"metric_name": "m1", "metric_label": "l1"}]
                }
        """
        host_list = list(data.keys())
        for host_id in host_list:
            if not all([detail.get(host_id), self.model.get(detail.get(host_id))]):
                continue
            model = self.model[detail[host_id]]
            if not model.calculate(data[host_id]):
                data.pop(host_id)

        return data

    def do_diag(self, detail: str, data: Dict[str, List[str]]) -> Tuple[str, str, str]:
        """
        Args:
            detail: it's a model id
            data: it's multi check result. e.g.
                {
                    "host1": [{"metric_name": "m1", "metric_label": "l1"}]
                }

        Returns:
            tuple: root host, root metric, root label
        """
        model = self.model.get(detail)
        if model is None:
            return "", "", ""

        return model.calculate(data)

    @staticmethod
    def format_result(multi_check_result: Dict[str, List[Dict[str, str]]], diag_result: Tuple[str, str, str]) -> Dict[
            str, List[Dict[str, str]]]:
        """
        Args:
            multi_check_result
            diag_result

        Returns:
            dict, e.g. {
                            "host1": [{
                                        "metric_name": "",
                                        "metric_label": "",
                                        "is_root": False
                                    }]
                        }
        """
        result = {}
        for host_id, metrics in multi_check_result.items():
            is_root = (host_id == diag_result[0])
            result[host_id] = []
            for metric in metrics:
                result[host_id].append({
                    "metric_name": metric['metric_name'],
                    "metric_label": metric['metric_label'],
                    "is_root": is_root and (metric['metric_name'] == diag_result[1]) and (
                        metric['metric_label'] == diag_result[2])
                })
        return result

    def execute(self, model_info: Dict[str, Dict[str, str]], detail: dict, data: dict) -> dict:
        """
        Args:
            model_info: it's information about model and algorithm. e.g.
                {
                    "model_id": {
                        "model_name": "",
                        "algo_id": "",
                        "algo_name": ""
                    }
                }
            detail: it's a map between metric and model. e.g.
                {
                    "singlecheck": {
                        "host1": {
                            "metric1": "model1",
                            "metric2": "model2"
                        }
                    },
                    "multicheck": {
                        "host1": "model3",
                        "host2": "model4"
                    },
                    "diag": "model5"
                }
            data: input original data. e.g.
                {
                    "host1": {
                        "metric1": [[time1, value1], [time2, value2]],
                        "metric2": [[time1, value1], [time2, value2]],
                        "metric3": [],
                        "metric4": None
                    },
                    "host2": None # no metric
                }

        Returns:
            dict, e.g. {
                "host_result": {
                    "host1": [
                        {
                            "metric_name": "",
                            "metric_label": "",
                            "is_root": False
                        }
                    ]
                },
                "alert_name": ""
            }
        """
        if not self.load_models(model_info):
            return {}

        signle_check_result = self.do_single_check(detail['singlecheck'], data)
        if not signle_check_result:
            return {}

        multi_check_result = self.do_multi_check(
            detail['multicheck'], signle_check_result)
        if not multi_check_result:
            return {}

        diag_result = self.do_diag(detail['diag'], multi_check_result)

        format_result = self.format_result(multi_check_result, diag_result)

        result = {
            "host_result": format_result,
            "alert_name": "network abnormal"
        }
        return result
