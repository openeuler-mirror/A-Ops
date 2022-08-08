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
Description: The implementation of hybrid model which is a multiple time-series model
"""

import time
from argparse import ArgumentError
from datetime import datetime, timedelta
from functools import reduce
from typing import Tuple, List

import numpy as np
import pandas as pd

from anteater.model.algorithms.normalization import Normalization
from anteater.model.algorithms.random_forest import RandomForest
from anteater.model.algorithms.vae import VAEPredict
from anteater.source.metric_loader import MetricLoader
from anteater.utils.config_parser import ModelSettings
from anteater.utils.data_process import load_metric_operator, parse_operator, metric_value_to_df
from anteater.utils.log import Log

log = Log().get_logger()


class HybridModel:
    """The hybrid model which aims to detect abnormal events
    based on multiple time series dataset.
    """

    def __init__(self, model) -> None:
        """The hybrid model initializer"""
        settings = ModelSettings()
        props = settings.hybrid_properties
        self.metric_operators = load_metric_operator()
        self.unique_metrics = set([m for m, _ in self.metric_operators])
        self.threshold = float(props["threshold"])
        self.model = model
        self.pipeline = self.select_pipe()

    def select_pipe(self):
        if self.model == "random_forest":
            return [
                ("classifier", RandomForest()),
            ]
        elif self.model == "vae":
            return [
                ("norm", Normalization()),
                ("classifier", VAEPredict()),
            ]
        else:
            raise ArgumentError(f"Unknow model name {self.model}.")

    def __get_dataframe(self, tim_start: datetime, tim_end: datetime) \
            -> Tuple[List[str], List[pd.DataFrame]]:
        """Gets the features during a period seperated by machine ids"""
        loader = MetricLoader(tim_start, tim_end)

        tim_run = time.time()
        machine_ids = loader.get_unique_label(self.unique_metrics, label_name="machine_id")
        log.info(f"Spends: {time.time() - tim_run} seconds to get unique machine_ids!")

        log.info(f"The number of unique machine ids is: {len(machine_ids)}!")

        tim_run = time.time()
        dataframes = []
        for machine_id in machine_ids:
            log.info(f"Fetch metric values from machine: {machine_id}.")

            metric_val_df = []
            for metric, operator in self.metric_operators:
                operator_name, operator_value = parse_operator(operator)
                labels, values = loader.get_metric(metric, label_name="machine_id", label_value=machine_id,
                                                   operator_name=operator_name, operator_value=operator_value)

                if len(labels) > 1 or len(values) > 1:
                    raise ValueError(f"Got multiple labels and values based on machine id,"
                                     f"len(labels): {len(labels)}, len(values): {len(values)}")

                values = values[0] if values else []

                col_name = f"{metric}-{operator}"
                metric_val_df.append(metric_value_to_df(values, col_name))

            df = reduce(lambda left, right: left.join(right, how='outer'), metric_val_df)
            df = df.fillna(0)

            dataframes.append(df)

        log.info(f"Spends: {time.time() - tim_run} seconds to get get all metric values!")

        return machine_ids, dataframes

    def predict(self, x):
        for pipe in self.pipeline[: -1]:
            x = pipe[1].transform(x)

        y_pred = self.pipeline[-1][1].predict(x)

        return y_pred

    def training(self, x):
        for pipe in self.pipeline[: -1]:
            x = pipe[1].fit_transform(x)

        self.pipeline[-1][1].fit(x)

    def is_abnormal(self, y_pred):
        """Checks if existing abnormal or not"""
        if isinstance(y_pred, np.ndarray):
            y_pred = y_pred.tolist()

        return sum(y_pred) >= len(y_pred) * self.threshold

    def get_training_data(self, utc_now: datetime):
        """Get the training data to support model training"""
        tim_start = utc_now - timedelta(days=1)
        tim_end = utc_now
        log.info(f"Get training data during {tim_start} to {tim_end}!")

        _, dfs = self.__get_dataframe(tim_start, tim_end)

        x_df = reduce(lambda left, right: pd.concat([left, right], axis=0), dfs)

        return x_df

    def get_inference_data(self, utc_now: datetime) -> Tuple[List[str], List[pd.DataFrame]]:
        """Get data for the model inference and prediction"""
        tim_start = utc_now - timedelta(minutes=1)
        tim_end = utc_now

        ids, dfs = self.__get_dataframe(tim_start, tim_end)

        return ids, dfs
