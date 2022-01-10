from typing import List

import requests

from spider.util.singleton import Singleton
from spider.collector.data_collector import DataCollector
from spider.collector.data_collector import DataRecord, Label


def generate_query_sql(metric_id: str, query_options: dict = None) -> str:
    if query_options is None:
        return metric_id

    sql = "{}{{".format(metric_id)
    for key, val in query_options.items():
        sql += "{key}=\"{val}\", ".format(key=key, val=val)
    sql += "}"
    return sql


class PrometheusCollector(DataCollector, metaclass=Singleton):
    def __init__(self, base_url: str = None, instant_api: str = None, range_api: str = None, step: int = None):
        super().__init__()
        self.base_url = base_url
        self.instant_api = instant_api
        self.range_api = range_api
        self.step = step

    def get_instant_data(self, metric_id: str, timestamp: float = None, **kwargs) -> List[DataRecord]:
        """
        从 Prometheus 获取指定时间戳的指标数据。
        例：
        输入：metric_id = "gala_gopher_task_fork_count", timestamp = 0
        输出：res = [
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=0, metric_value=1,
                            labels=[Label(name="machine_id", value="machine1")]),
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=0, metric_value=2,
                            labels=[Label(name="machine_id", value="machine2")]),
             ]
        @param metric_id: 指标的ID
        @param timestamp: 查询指定时间戳的数据
        @param kwargs: 查询条件可选项
        @return: 指定时间戳的指标数据的 DataRecord 列表。
        """
        data_list = []
        query_options = kwargs.get("query_options") if "query_options" in kwargs else None
        params = {
            "query": generate_query_sql(metric_id, query_options),
        }
        if timestamp is not None:
            params["time"] = timestamp

        url = self.base_url + self.instant_api
        try:
            rsp = requests.get(url, params).json()
        except requests.RequestException:
            print("An error happened when requesting {}".format(url))
            return data_list

        if rsp is not None and rsp.get("status") == "success":
            results = rsp.get("data", {}).get("result", [])
            for item in results:
                metric = item.get("metric", {})
                value = item.get("value", [])
                if not metric or not value:
                    continue
                labels = [Label(k, v) for k, v in metric.items()]
                data_list.append(DataRecord(metric_id, value[0], value[1], labels))
        return data_list

    def get_range_data(self, metric_id: str, start: float, end: float, **kwargs) -> List[DataRecord]:
        """
        从 Prometheus 获取指定时间范围 [start, end] 的指标数据。
        例：
        输入：metric_id = "gala_gopher_task_fork_count", start = 0, end = 1
        输出：res = [
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=0, metric_value=1,
                            labels=[Label(name="machine_id", value="machine1")]),
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=1, metric_value=2,
                            labels=[Label(name="machine_id", value="machine1")]),
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=0, metric_value=1,
                            labels=[Label(name="machine_id", value="machine2")]),
                 DataRecord(metric_id="gala_gopher_task_fork_count", timestamp=1, metric_value=2,
                            labels=[Label(name="machine_id", value="machine2")]),
             ]
        @param metric_id: 指标的ID
        @param start: 起始时间戳（包含）
        @param end: 结束时间戳（包含）
        @param kwargs: 查询条件可选项
        @return: 指定时间范围 [start, end] 的指标数据
        """
        data_list = []
        query_options = kwargs.get("query_options") if "query_options" in kwargs else None
        step = kwargs.get("step") if "step" in kwargs else self.step
        params = {
            "query": generate_query_sql(metric_id, query_options),
            "start": start,
            "end": end,
            "step": step
        }

        url = self.base_url + self.range_api
        try:
            rsp = requests.get(url, params).json()
        except requests.RequestException:
            print("An error happened when requesting {}".format(url))
            return data_list

        if rsp is not None and rsp.get("status") == "success":
            results = rsp.get("data", {}).get("result", [])
            for item in results:
                metric = item.get("metric", {})
                values = item.get("values", [])
                if not metric or not values:
                    continue
                labels = [Label(k, v) for k, v in metric.items()]
                for value in values:
                    data_list.append(DataRecord(metric_id, value[0], value[1], labels))
        return data_list
