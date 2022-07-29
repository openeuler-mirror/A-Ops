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
Description: The base class for prediction model.
"""

from abc import ABC, abstractmethod


class Predict(ABC):
    """
    The base model will be used to predict.
    """
    def __init__(self, model_path, threshold, *args, **kwargs):
        """The base class initializer"""
        self.model_path = model_path
        self.threshold = threshold
        self.model = None

    @abstractmethod
    def load_model(self):
        """load model"""
        pass

    @abstractmethod
    def predict(self, x):
        """predict based on model"""
        pass

    def is_abnormal(self, y_pred):
        """
        Checks if existing abnormal or not
        :param y_pred: The predicted label
        :return: Existing abnormal points or not
        """
        return sum(y_pred) >= len(y_pred) * self.threshold
