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
import os

import joblib

from anteater.utils.common import get_file_path
from anteater.utils.settings import ModelSettings
from anteater.utils.log import Log

log = Log().get_logger()


class RandomForest:
    """
    The random forest predict model.
    """
    def __init__(self):
        """The random forest model initializer"""
        settings = ModelSettings()
        props = settings.rf_properties
        self.model_path = get_file_path(props["file_name"])
        self.threshold = float(props["threshold"])

        self.model = self.load_model()

    def load_model(self):
        """Loads random forest model"""
        if not os.path.isfile(self.model_path):
            raise FileExistsError("Fandom forest model file was not found! "
                                  "lease provide the model binary file in advance!")

        return joblib.load(self.model_path)

    def predict(self, x):
        """Predicts the anomaly score by random forest model"""
        y_pred = self.model.predict(x)

        return y_pred
