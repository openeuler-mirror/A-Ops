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

from datetime import datetime, timedelta, timezone
from functools import reduce
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from utils.common import load_prometheus_client, save_normalizer
from utils.log import Log

log = Log().get_logger()

# network metric names
network_metrics = [
    "gala_gopher_ksliprobe_recent_rtt_nsec",
    "gala_gopher_ksliprobe_max_rtt_nsec",
    "gala_gopher_ksliprobe_min_rtt_nsec",
    "gala_gopher_tcp_link_info_notsent_bytes",
    "gala_gopher_tcp_link_info_notack_bytes",
    "gala_gopher_tcp_link_info_srtt",
    "gala_gopher_tcp_link_info_rcv_rtt",
    "gala_gopher_tcp_link_info_syn_srtt_last",
    "gala_gopher_tcp_link_info_delivery_rate",
    "gala_gopher_tcp_link_info_pacing_rate",
    "gala_gopher_tcp_link_info_max_pacing_rate"
]


# network metric names
disk_metrics = [
    "gala_gopher_block_latency_flush_jitter",
    "gala_gopher_block_latency_flush_last",
    "gala_gopher_block_latency_flush_max",
    "gala_gopher_block_latency_req_jitter",
    "gala_gopher_block_latency_req_max",
    "gala_gopher_block_latency_req_last",
]


def get_filter_rule(metric, **unique_id) -> Dict[str, any]:
    """
    Generates filtering rule based on the arguments, and parse to json format.
    :param metric: The metric name
    :param tgid: The tgid
    :param machine_id: The machine id
    :param server_ip: The server ip
    :param server_port: The server port
    :param client_ip: The client ip
    :param client_port: The client port
    :return: The json object of filtering rule.
    """
    if metric in network_metrics:
        rule = unique_id
    elif metric in disk_metrics:
        server_ip = unique_id.get("server_ip", "")
        rule = {
            "blk_name": "sda",
            "blk_type": "disk",
            "job": f"prometheus-{server_ip}",
            "instance": f"{server_ip}:8888"
        }
    else:
        raise ValueError("The metric name is not in the network or disk metrics set.")

    return rule


def get_training_data():
    """
    Get the training data to support model training.
    :return: the normalized unlabeled training data
    """
    utc_now = datetime.now(timezone.utc).astimezone().replace(second=0, microsecond=0)
    start_time = utc_now - timedelta(days=1)
    end_time = utc_now

    log.info(f"Get training data during {start_time} to {end_time}!")
    metrics_loader = MetricsLoader(start_time, end_time)
    features = metrics_loader.extract_features()

    feature_df = []
    for _, df in features:
        feature_df.append(df)

    x_df = reduce(lambda left, right: pd.concat([left, right], axis=0), feature_df)

    scaler = StandardScaler()
    x_norm = scaler.fit_transform(x_df)

    save_normalizer(scaler)

    return x_norm


class MetricsLoader:
    """
    The metric loader that consumes raw data from Prometheus,
    then convert them to dataframe
    """
    def __init__(self, start_time, end_time):
        """
        The Metrics Loader initializer
        :param start_time: The start time
        :param end_time: The end time
        """
        self.prometheus = load_prometheus_client()
        self.start_time = start_time
        self.end_time = end_time

    def extract_features(self):
        """Extracts the features during start time and end time."""
        metrics = network_metrics + disk_metrics

        unique_ids = self.prometheus.get_unique_ids(self.start_time, self.end_time, metrics)

        features = []
        for unique_id in unique_ids:
            features_df = []
            for metric in metrics:
                rules = get_filter_rule(metric, **unique_id)
                data = self.prometheus.query_data(self.start_time, self.end_time, metric, True, **rules)

                if not data:
                    features_df.append(
                        pd.DataFrame(columns=["timestamp", metric], dtype=object).set_index("timestamp"))
                else:
                    agg_data = []
                    for item in data:
                        for value in item['values']:
                            agg_data.append(
                                {'timestamp': datetime.fromtimestamp(value[0]), metric: np.float64(value[1])})

                    features_df.append(pd.DataFrame(agg_data).set_index("timestamp"))

            df = reduce(lambda left, right: left.join(right, how='outer'), features_df)
            df = df.fillna(0)
            features.append((unique_id, df))

        return features
