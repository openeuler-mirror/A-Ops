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
import functools
from importlib import import_module

from aops_utils.log.log import LOGGER


@functools.lru_cache()
def load_model(model_id: str, model_path: str, algo_path: str) -> object:
    try:
        # aops_check.core.experiment.algorithm.diag.Diag
        # module_path: aops_check.core.experiment.algorithm.diag
        # param_name: Diag
        [module_path, param] = algo_path.rsplit('.', 1)
        module = import_module(module_path)
        # get algorithm class and instantiate it
        model = module.__dict__[param]()
        if model_path:
            model.load(model_path)
        LOGGER.debug(f"load model {model_id} succeed")
    except (ModuleNotFoundError, TypeError, KeyError) as error:
        model = None
        LOGGER.error(error)
        LOGGER.error(f"load model {model_id} fail")
    finally:
        return model
