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
Description: The implementation of metrics data loader.
"""

from typing import List, Tuple, Dict, Union

from anteater.utils.common import load_prometheus_client
from anteater.utils.log import Log

log = Log().get_logger()


def get_query(metric: str,
              label_name: Union[str, List] = None, label_value: Union[str, List] = None,
              operator_name: str = None, operator_value: float = None):
    """Gets aggregated query patterns

        Such as:
            - 1. gala_gopher_bind_sends{machine_id="1234"}
            - 2. sum(gala_gopher_bind_sends) by (machine_id)
            - 3. sum(gala_gopher_bind_sends{machine_id="1234"}) by (machine_id)
            - 4. quantile(0.7, gala_gopher_bind_sends{machine_id="1234"}) by (machine_id)
    """
    rule = ""
    if label_value:
        if type(label_name) != type(label_value):
            raise ValueError(f"The label_name and label_value are of different types,"
                             f"type(label_name): {type(label_name)},"
                             f"type(label_value): {type(label_value)}.")
        if isinstance(label_value, list):
            pairs = ",".join([f"{n}='{v}'" for n, v in zip(label_name, label_value)])
            rule = f"{{{pairs}}}"
        elif isinstance(label_value, str):
            rule = f"{{{label_name}='{label_value}'}}"

    group = ""
    if isinstance(label_name, list):
        group = ",".join([k for k in label_name])
    elif isinstance(label_name, str):
        group = label_name

    if operator_name and operator_value:
        query = f"{operator_name}({operator_value}, {metric}{rule}) by ({group})"
    elif operator_name:
        query = f"{operator_name}({metric}{rule}) by ({group})"
    else:
        query = f"{metric}{rule}"

    return query


class MetricLoader:
    """
    The metric loader that consumes raw data from Prometheus,
    then convert them to dataframe
    """

    def __init__(self, start_time, end_time) -> None:
        """The Metrics Loader initializer"""
        self.prometheus = load_prometheus_client()
        self.start_time = start_time
        self.end_time = end_time

    def get_metric(self, metric: str, **kwargs)\
            -> Tuple[List[Dict], List[List[List]]]:
        """Get target metric values

        :kwargs
            - label_name: Union[str, List] = None,
            - label_value: Union[str, List] = None,
            - operator_name: str = None,
            - operator_value: float = None)

        :return Tuple of labels and values
            labels:
                - [{"__name__": gala_gopher_.*, "machine_id": "12345"}, ...]
            values:
                - [[[1234, "1"], [1235, "2"], [1236, "2.6"], ...], ...]
        """
        labels = []
        values = []
        query = get_query(metric, **kwargs)
        data = self.prometheus.range_query(self.start_time, self.end_time, query)
        for item in data:
            labels.append(item["metric"])
            values.append(item["values"])

        return labels, values

    def get_unique_label(self, metrics, label_name) -> List:
        """Gets unique labels of all metrics"""
        unique_labels = set()
        for metric in metrics:
            labels, _ = self.get_metric(metric, label_name=label_name)
            unique_labels.update([lbl.get(label_name, "") for lbl in labels])

        return list(unique_labels)

    def expected_point_length(self) -> int:
        """Gets expected length of time series during a period"""
        start, end = round(self.start_time.timestamp()), round(self.end_time.timestamp())
        if self.prometheus.step >= 0:
            return max((end - start) // self.prometheus.step, 1)
        else:
            return 0
