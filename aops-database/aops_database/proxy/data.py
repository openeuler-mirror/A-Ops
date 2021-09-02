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
Description: Check database operation
"""

from collections import defaultdict

from aops_database.proxy.proxy import ElasticsearchProxy, PromDbProxy
from aops_database.function.helper import judge_return_code, timestamp_datetime, timestr_unix
from aops_utils.restful.status import DATABASE_QUERY_ERROR, PARTIAL_SUCCEED
from aops_utils.log.log import LOGGER


class LogDatabase(ElasticsearchProxy):
    """
    Log data from server
    """

    def get_data(self, args):
        """
        Get log data from elasticsearch
        Args:
            args (dict): e.g.
            {
                "time_range": [1111,2222],
                "data_infos": [
                    {
                        "host_id": "1.1.1.1",
                        "data_list": ["messages", "history"]
                    }，
                    {
                        "host_id": "1.1.1.2",
                        "data_list": ["name": "messages"]
                    }
                ]
            }

        Returns:
            tuple: (int, dict)
        """
        start_time = timestamp_datetime(args["time_range"][0])
        end_time = timestamp_datetime(args["time_range"][1])
        hosts_info = args["data_infos"]

        success_result = []
        failed_result = []

        doc = {
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"data_item": []}},
                        {"range": {"@timestamp": {"gte": start_time, "lte": end_time}}}
                    ]
                }
            }
        }

        for host_info in hosts_info:
            host_id = host_info["host_id"]
            data_items = host_info["data_list"]

            doc["query"]["bool"]["must"][0]["terms"]["data_item"] = data_items
            query_flag, query_result = self.scan(host_id, doc)

            # query succeed
            if query_flag:
                success_result.extend(LogDatabase._parse_data(host_id, query_result))
            # query failed
            else:
                failed_result.extend({"host_id": host_id, "data_items": data_items})

        data = {"succeed_list": success_result, "fail_list": failed_result}

        status_code = judge_return_code(data, DATABASE_QUERY_ERROR)

        if status_code in (PARTIAL_SUCCEED, DATABASE_QUERY_ERROR):
            LOGGER.error("Query log data failed with status code %d.", status_code)
        else:
            LOGGER.info("Query log data succeed.")

        return status_code, data

    @staticmethod
    def _parse_data(host_id, query_result):
        """
        parse data into the format designed
        Args:
            host_id: host's ip
            query_result: query result from es

        Returns:
            list
        """
        data = []

        data_value_dict = defaultdict(list)

        for single_piece_data in query_result:
            timestamp = timestr_unix(single_piece_data["@timestamp"])
            data_item = single_piece_data["data_item"]
            message = single_piece_data["message"]

            data_value_dict[data_item].append([timestamp, message])

        for data_name, data_val in data_value_dict.items():
            sorted_value = sorted(data_val, key=lambda item: item[0])
            parsed_data = {"host_id": host_id, "name": data_name, "values": sorted_value}

            data.append(parsed_data)

        return data


class KpiDataBase(PromDbProxy):
    """
    Kpi data from server
    """

    def get_data(self, args):
        """
        Get kpi data from prometheus's time series database
        Args:
            args (dict):
                {
                    "time_range": [1111,2222],
                    "data_infos": [
                        {
                            "host_id": "host1",
                            "data_list": [
                                {
                                    "name": "node_cpu",
                                    "label": {
                                        "cpu": "cpu1",
                                        "mode": "idle"
                                    }
                                },
                                {
                                    "name": "node_memory"
                                }
                            ]
                        }
                    ]
                }
        Returns:
            tuple: (int, dict)
        """
        time_range = args["time_range"]
        hosts_info = args["data_infos"]

        success_result = []
        failed_result = []

        for host_info in hosts_info:
            host_id = host_info["host_id"]
            data_items = host_info["data_list"]

            for data_item in data_items:
                query_flag, query_result = self.query(host_id, time_range, data_item["name"],
                                                      data_item.get("label"))

                # query succeed
                if query_flag:
                    try:
                        success_result.extend(KpiDataBase._parse_data(query_result))
                    except KeyError as error:
                        failed_result.extend(query_result)
                        LOGGER.error("Prometheus api changed interface, doesn't have "
                                     "the key %s in query result." % error)
                # query failed
                else:
                    failed_result.extend(query_result)

        data = {"succeed_list": success_result, "fail_list": failed_result}

        status_code = judge_return_code(data, DATABASE_QUERY_ERROR)

        if status_code in (PARTIAL_SUCCEED, DATABASE_QUERY_ERROR):
            LOGGER.error("Query kpi data failed with status code %d.", status_code)
        else:
            LOGGER.info("Query kpi data succeed.")

        return status_code, data

    @staticmethod
    def _parse_data(query_result):
        """
        parse data into the format designed
        Args:
            query_result: pieces of metric data with specific labels
            e.g.:
                [{
                    "metric":
                        {
                            "__name__": "node_cpu_seconds_total",
                            "cpu": "1",
                            "instance": "1.1.1.1:9100",
                            "job": "node",
                            "mode": "idle"
                        },
                    "values": [[1629169987.931, "1187112.68"], [1629169999.931, "1187123.68"]]
                },
                {
                    "metric":
                        {
                            "__name__": "node_cpu_seconds_total",
                            "cpu": "1",
                            "instance": "1.1.1.1:9100",
                            "job": "node",
                            "mode": "iowait"
                        },
                    "values": [[1629169987.931, "3.68"], [1629169999.931, "2.68"]]
                }]
        Returns:
            dict
        """
        data = []

        for single_piece_data in query_result:
            metric_data = single_piece_data["metric"]
            values = single_piece_data["values"]
            default_ket_set = {"__name__", "instance", "job"}
            label_config = {}

            # list all label config including the assigned label config
            for key, value in metric_data.items():
                if key not in default_ket_set:
                    label_config[key] = value

            host_ip = metric_data["instance"].split(":")[0]
            metric_name = metric_data["__name__"]

            parsed_data = {
                "host_id": host_ip,
                "name": metric_name,
                "label": label_config,
                "values": values
            }

            data.append(parsed_data)

        return data
