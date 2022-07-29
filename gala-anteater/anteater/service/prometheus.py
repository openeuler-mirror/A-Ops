#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
Description: The implementation of Prometheus client to fetch time series data.
"""

from datetime import datetime, timedelta
from tracemalloc import start

import requests

from utils.log import Log

log = Log().get_logger()


class Prometheus:
    """
    The Prometheus client to consume time series data.
    """
    def __init__(self, server, port, step=5, interval_hours=6):
        """
        The Prometheus client initializer
        :param server: The prometheus server ip
        :param port: The prometheus server port
        :param step: The query time interval (seconds)
        :param interval_hours: The hours of interval for batch processing
        """
        self.query_url = f"http://{server}:{port}/api/v1/query_range"
        self.step = step
        self.interval_hours = interval_hours

    @staticmethod
    def chunks(start_time, end_time, hours=6):
        """
        Split a duration (from start time to end time) to multi-disjoint intervals
        :param start_time: The start time
        :param end_time: The end time
        :param hours: The interval hours
        :return: The split disjoint intervals
        """
        if (start_time >= end_time):
            raise ValueError("The start_time greater or equal than end_time!")

        if not isinstance(start_time, datetime):
            raise ValueError("The type of start_time isn't datetime!")

        if not isinstance(end_time, datetime):
            raise ValueError("The type of end_time isn't datetime!")

        _start = start_time
        _end = _start
        while _end < end_time:
            _end = min(_start + timedelta(hours=hours), end_time)
            yield _start, _end
            _start = _end

    def query_data(self, start_time, end_time, metric, is_aggregate=False, **kwargs):
        """
        Fetches the time series data from Prometheus.
        :param start_time: The start time
        :param end_time: The end time
        :param metric: The metric name
        :param is_aggregate: Is aggregate the results
        :param kwargs: The kwargs
        :return: The fetched data
        """
        filter_rules = "{" + ",".join([f"{k}='{v}'" for k, v in kwargs.items()]) + "}"
        if is_aggregate:
            query = f"avg({metric}{filter_rules}) by ({','.join([str(k) for k in kwargs.keys()])})"
        else:
            query = f"{metric}{filter_rules}"

        data = []
        for _start, _end in self.chunks(start_time, end_time, self.interval_hours):
            _start, _end = round(_start.timestamp()), round(_end.timestamp())
            params = {
                "query": query,
                "start": _start,
                "end": _end,
                "step": self.step
            }

            response = requests.get(self.query_url, params).json()

            if response["status"] == 'success':
                for item in response.get("data", []).get("result", []):
                    data.append(item)
            else:
                log.info("Prometheus get data failed! Error: {}.".format(response["error"]))

        return data

    def get_unique_ids(self, start_time, end_time, metrics):
        """
        Gets the unique ids corresponding to the metrics
        :param start_time: The start time
        :param end_time: The end time
        :param metrics: The metrics
        :return: The unique ids
        """
        unique_tgids = self.get_unique_tgids(start_time, end_time)

        unique_ids = []
        for metric in metrics:
            data = self.query_data(start_time, end_time, metric)
            for item in data:
                info = item["metric"]
                tgid = info.get("tgid", None)

                if tgid not in unique_tgids:
                    break

                machine_id = info.get("machine_id", None)
                server_ip = info.get("server_ip", None)
                server_port = info.get("server_port", None)
                client_ip = info.get("client_ip", None)
                client_port = info.get("client_port", None)

                if not (machine_id and server_ip and server_port):
                    log.info("The tgid, machine id, server ip or server port is null!")

                if (tgid, machine_id, server_ip, server_port, client_ip, client_port) not in unique_ids:
                    unique_ids.append((tgid, machine_id, server_ip, server_port, client_ip, client_port))

        return [{
            "tgid": value[0],
            "machine_id": value[1],
            "server_ip": value[2],
            "server_port": value[3],
            "client_ip": value[4],
            "client_port": value[5]
        } for value in unique_ids]

    def get_unique_tgids(self, start_time, end_time):
        """
        Gets the unique tgids from Prometheus
        :param start_time: The start time
        :param end_time: The end time
        :return: The unique tgids
        """
        target_metric = "gala_gopher_system_proc_proc_read_bytes"
        filter_rule = {"comm": "redis-server"}
        data = self.query_data(start_time, end_time, target_metric, **filter_rule)

        unique_tgids = set()

        for item in data:
            tgid = item["metric"].get("tgid", None)

            if not tgid:
                raise ValueError("The tgid, machine id, server ip or server port is null!")

            if tgid not in unique_tgids:
                unique_tgids.add(tgid)

        return unique_tgids
