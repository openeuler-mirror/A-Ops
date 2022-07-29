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
Description: The data processors of raw metric datasets.
"""

import os
from datetime import datetime
from os import path
from typing import List, Tuple, Union

import numpy as np
import pandas as pd

from anteater.utils.log import Log

log = Log().get_logger()


def metric_value_to_df(value: List[List], col_name: str):
    """Converts 2-dim values to the dataframe
        values:
            - [[1234, "1"], [1235, "2"], [1236, "2.6"], ...]
    """
    if not value:
        return pd.DataFrame(columns=["timestamp", col_name], dtype=object).set_index("timestamp")

    data = []
    for tim, val in value:
        data.append({"timestamp": datetime.fromtimestamp(tim), col_name: np.float32(val)})

    df = pd.DataFrame(data).set_index("timestamp")
    df = df[~df.index.duplicated()]

    return df


def load_metric_operator():
    """Loads metric name and corresponding operator"""
    folder_path = path.dirname(path.dirname(path.realpath(__file__)))
    metrics_file = path.join(folder_path, os.sep.join(["model", "observe", "metrics.csv"]))

    log.info(f"Loads metric and operators from file: {metrics_file}")

    metric_operators = []
    with open(metrics_file, 'r', encoding='utf-8') as f:
        for line in f:
            metric_name, operator = line.strip().split(",")
            metric_operators.append((metric_name, operator))

    return metric_operators


def parse_operator(operator: str) -> Tuple[str, Union[float, None]]:
    """Parses operator string to the name and value

        Such as:
        - sum -> sum, None
        - avg -> avg, None
        - quantile_1 -> quantile, 0.7
        - quantile_2 -> quantile, 0.3
    """
    if operator == "quantile_1":
        return "quantile", 0.7
    elif operator == "quantile_2":
        return "quantile", 0.3
    return operator, 0
