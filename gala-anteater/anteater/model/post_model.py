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
Description: The post process which aims to find the top n anomalies.
"""

import math
from datetime import datetime, timedelta
from typing import List, Tuple, Any

import numpy as np

from anteater.model.algorithms.spectral_residual import SpectralResidual
from anteater.utils.data_process import load_metric_operator
from anteater.source.metric_loader import MetricLoader


class PostModel:
    """The post model which aims to recommend some key metrics for abnormal events"""

    def __init__(self) -> None:
        """The post model initializer"""
        self.metric_operators = load_metric_operator()
        self.unique_metrics = set([m for m, _ in self.metric_operators])

    @staticmethod
    def predict(sr_model: SpectralResidual, values: List) -> float:
        """Predicts anomalous score for the time series values"""
        if all(x == values[0] for x in values):
            return -math.inf

        scores = sr_model.compute_score(values)

        return max(scores[-12: -1])

    def get_all_metric(self, loader, machine_id: str):
        """Gets all metric labels and values"""
        labels, values = [], []
        for metric in self.unique_metrics:
            label, value = loader.get_metric(metric, label_name="machine_id", label_value=machine_id)
            labels.extend(label)
            values.extend(value)

        return labels, values

    def top_n_anomalies(self, utc_now: datetime, machine_id: str, top_n: int) -> List[Tuple[Any, dict, Any]]:
        """Finds top n anomalies during a period for the target machine"""
        tim_start = utc_now - timedelta(minutes=6)
        tim_end = utc_now

        loader = MetricLoader(tim_start, tim_end)
        labels, values = self.get_all_metric(loader, machine_id)

        point_count = loader.expected_point_length()

        sr_model = SpectralResidual(12, 24, 50)

        scores = []
        for label, value in zip(labels, values):
            if len(value) < point_count * 0.9 or\
               len(value) > point_count * 1.5:
                continue

            target_value = [np.float64(v[1]) for v in value]
            score = self.predict(sr_model, target_value)

            if math.isnan(score) or math.isinf(score):
                continue

            scores.append((label["__name__"], label, score))

        sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)

        return sorted_scores[0: top_n]
