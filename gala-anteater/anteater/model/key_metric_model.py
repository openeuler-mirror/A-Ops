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
Description: The key metric model which aims to do the anomaly detection for key metrics.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Any

import numpy as np
import pandas as pd

from anteater.source.metric_loader import MetricLoader
from anteater.utils.settings import MetricSettings
from anteater.utils.log import Log

log = Log().get_logger()


class KeyMetricModel:
    """The key metric model which will detect key metric is anomaly or not"""

    def __init__(self):
        """The post model initializer"""
        settings = MetricSettings()
        self.key_metric = settings.key_metric_name

    @staticmethod
    def predict(x: List) -> float:
        """Predicts anomalous score for the time series values"""
        if isinstance(x, pd.DataFrame):
            y_pred = x.mean(axis=1).to_numpy().flatten()
        elif isinstance(x, np.ndarray):
            y_pred = x.mean(axis=1).flatten()
        else:
            y_pred = np.mean(x)

        return y_pred

    def detect_key_metric(self, utc_now: datetime, machine_id: str) -> List[Tuple[Any, dict, Any]]:
        """Detects key metric by rule-based model"""
        tim_start = utc_now - timedelta(minutes=1)
        tim_end = utc_now

        metric_loader = MetricLoader(tim_start, tim_end)

        labels, values = metric_loader.get_metric(self.key_metric, label_name="machine_id", label_value=machine_id)

        if not labels or not values:
            log.error(f"Key metric {self.key_metric} is null on the target machine {machine_id}!")

        scores = []
        for label, value in zip(labels, values):
            target_value = [np.float64(v[1]) for v in value]
            score = self.predict(target_value)

            scores.append((label["__name__"], label, score))

        sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)
        anomalies = [s for s in sorted_scores if round(s[2]/1000000) > 200]

        return anomalies[:3] if anomalies else sorted_scores[:1]

