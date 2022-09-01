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
from copy import deepcopy
from importlib import import_module
from typing import Dict, List, Any

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import SUCCEED
from aops_check.conf.constant import ALGO_LIST
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

    @staticmethod
    def _turn_algo_list_to_dict(algo_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
        """
        turn algo_list to target dict type

        Returns:
            dict: e.g
                {
                    model_id:{
                       'model_path':'string',
                       'algo_module':'string'
                    },
                    ...
                }
        """
        models = {}
        for algo in algo_list:
            for model in algo['models']:
                models[model['model_id']] = {
                    'model_path': model['file_path'],
                    'algo_module': algo['algo_module']
                }
        return models

    def _load_models_for_default(self, model_info: Dict[str, dict]) -> Dict[str, dict]:
        """
            get model path and algorithm path by model id.

        Returns:
            dict: e.g
                {
                    "model_id":
                        {
                            "model_path": string,
                            "algo_module": string
                        }
                        ...
                }
        """

        algo_path_info = {}

        all_model = self._turn_algo_list_to_dict(ALGO_LIST)

        models = {}
        for model_id in model_info.keys():
            if model_id not in all_model:
                LOGGER.debug('System has no such model %s' % model_id)
                continue

            if all_model[model_id]['algo_module'] in algo_path_info:
                algo_path = algo_path_info[all_model[model_id]['algo_module']]

            else:
                algo = all_model[model_id]
                module_path, class_name = algo["algo_module"].rsplit('.', 1)
                algo_module = import_module('.', module_path)
                class_ = getattr(algo_module, class_name)
                algo_path = deepcopy(class_().info)['path']

            models[model_id] = {
                'model_path': all_model[model_id]['model_path'],
                'algo_path': algo_path
            }

        return models

    def load_models(self, model_info: Dict[str, dict], default_mode: bool = False) -> bool:
        """
        1. Check model first, return directly if don't need load model again.
        2. connect to database, get model path and algorithm path
        3. load model
        """
        if self.check_model(self.model, model_info):
            return True

        if default_mode:
            models = self._load_models_for_default(model_info)

        else:
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
