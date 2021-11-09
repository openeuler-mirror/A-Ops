from typing import List

import requests

from spider.collector.data_collector import DataCollector
from spider.collector.data_collector import DataRecord, Label
from spider.util.conf import prometheus_conf


def generate_query_sql(metric_id: str, query_options: dict = None) -> str:
    if query_options is None:
        return metric_id

    sql = "{}{{".format(metric_id)
    for key, val in query_options.items():
        sql += "{key}=\"{val}\", ".format(key=key, val=val)
    sql += "}"
    return sql


class PrometheusCollector(DataCollector):
    def __init__(self, base_url: str, instant_api: str, range_api: str = None, step=1):
        super().__init__()
        self.base_url = base_url
        self.instant_api = instant_api
        self.range_api = range_api
        self.step = step

    def get_instant_data(self, metric_id: str, timestamp: float = None, **kwargs) -> List[DataRecord]:
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

        if rsp.get("status") == "success":
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

        if rsp.get("status") == "success":
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


# init global prometheus collector
g_prometheus_collector = PrometheusCollector(base_url=prometheus_conf.get("base_url"),
                                             instant_api=prometheus_conf.get("instant_api"),
                                             range_api=prometheus_conf.get("range_api"))
if prometheus_conf.get("step") is not None:
    g_prometheus_collector.step = prometheus_conf.get("step")
