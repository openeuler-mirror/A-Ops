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
from typing import List, Dict, Union

import requests

from anteater.utils.log import Log

log = Log().get_logger()


class Prometheus:
    """The Prometheus client to consume time series data"""

    def __init__(self, server, port, step=5):
        """The Prometheus client initializer"""
        self.server = server
        self.port = port
        self.step = step

    @staticmethod
    def chunks(start_time, end_time, hours=6):
        """Split a duration (from start time to end time) to multi-disjoint intervals"""
        if start_time >= end_time:
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

    @staticmethod
    def fetch(query_url, params: Dict = None) -> Union[List, Dict]:
        """Fetches data from prometheus server by http request"""
        response = requests.get(query_url, params).json()
        if response["status"] != 'success':
            log.error(f"Prometheus get data failed, "
                      f"error: {response['error']}, query_url: {query_url}, params: {params}.")
            return {}

        return response["data"]

    def get_unique_labels(self, label: str) -> List:
        """Gets the unique labels"""
        query_url = f"http://{self.server}:{self.port}/api/v1/label/{label}/values"
        data = self.fetch(query_url)

        return data

    def range_query(self, start_time: datetime, end_time: datetime, query: str) -> List[Dict]:
        """Range query time series data from Prometheus"""
        query_url = f"http://{self.server}:{self.port}/api/v1/query_range"
        result: List[Dict] = []
        tmp_index = {}
        for start, end in self.chunks(start_time, end_time):
            start, end = round(start.timestamp()), round(end.timestamp())
            params = {
                "query": query,
                "start": start,
                "end": end,
                "step": self.step
            }

            data = self.fetch(query_url, params)

            for metric_value in data.get("result", {}):
                key = tuple(sorted(metric_value.get("metric").items()))
                if key in tmp_index:
                    result[tmp_index.get(key)]["values"].extend(metric_value.get("values"))
                else:
                    tmp_index[key] = len(result)
                    result.append(metric_value)

        return result
