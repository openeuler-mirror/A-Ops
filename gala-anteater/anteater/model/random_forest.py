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
Description: The random forest prediction model which was trained offline
and will be used to predict online.
"""

from random import sample
import joblib

from model.base import Predict


class RandomForestPredict(Predict):
    """
    The random forest predict model.
    """
    def __init__(self, model_path, threshold, *args, **kwargs):
        """
        The random forest model initializer.
        :param model_path: The model path
        :param threshold: The threshold of model score
        :param args: The args
        :param kwargs: The kwargs
        """
        super().__init__(model_path, threshold, *args, **kwargs)

    def load_model(self):
        """Loads random forest model"""
        return joblib.load(self.model_path)

    def predict(self, x):
        """Predicts the anomaly score by random forest model"""
        self.model = self.load_model()
        y_pred = self.model.predict(x)

        return y_pred
