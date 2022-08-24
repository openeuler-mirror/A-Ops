#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
from typing import Dict

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import SUCCEED

from aops_check.core.experiment.model import load_model
from aops_check.database import SESSION
from aops_check.database.dao.model_dao import ModelDao


class App:
    def __init__(self):
        self.model = {}

    def load_detail(self):
        ...

    @staticmethod
    def check_model(model: Dict[str, object], model_info: Dict[str, dict]) -> bool:
        """
        Check whether all models have been loaded.
        """
        for model_id in model_info:
            if model_id not in model:
                return False

        return True

    def load_models(self, model_info: Dict[str, dict]) -> bool:
        """
        1. Check model first, return directly if don't need load model again.
        2. connect to database, get model path and algorithm path
        3. load model
        """
        if self.check_model(self.model, model_info):
            return True

        model_dao = ModelDao()
        if not model_dao.connect(SESSION):
            LOGGER.error("connect to database fail")
            return False

        model_list = list(model_info.keys())
        status_code, models = model_dao.get_model(model_list)
        if status_code != SUCCEED:
            return False

        for model_id, path_info in models.items():
            model = load_model(model_id, path_info['model_path'], path_info['algo_path'])
            if model is None:
                return False
            self.model[model_id] = model

        return True

    def execute(self, **kwargs):
        ...
