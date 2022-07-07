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
Description: Select corresponding model based model name
"""

from model.base import Predict
from model.random_forest import RandomForestPredict
from model.vae import VAEPredict
from utils.config_parser import ModelSettings


def select_model(name: str) -> Predict:
    """
    Select model and parse parameters in it.

    :param name: The model name
    :return: The Prediction model.
    """
    settings = ModelSettings()
    if name == "random_forest":
        props = settings.random_properties
        path = props["path"]
        threshold = float(props["threshold"])

        return RandomForestPredict(path, threshold)

    elif name == "vae":
        props = settings.vae_properties
        path = props["path"]
        thr = float(props["threshold"])
        retrain = bool(props["retrain"])

        return VAEPredict(path, thr, retrain)
    else:
        raise ValueError(f"unknown dataset: {name}")