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
import sqlalchemy
import uuid
from copy import deepcopy
from importlib import import_module

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_INSERT_ERROR
from aops_check.database import SESSION
from aops_check.database.dao.algo_dao import AlgorithmDao
from aops_check.database.dao.model_dao import ModelDao


algo_list = [
    {
        "algo_module": "aops_check.core.experiment.algorithm.single_item_check.ewma.EWMA",
        "models": [{
            "model_id": "Ewma-1",
            "model_name": "Ewma",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": None,
            "precision": None
        }]
    },
    {
        "algo_module": "aops_check.core.experiment.algorithm.single_item_check.mae.Mae",
        "models": [{
            "model_id": "Mae-1",
            "model_name": "Mae",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": None,
            "precision": None
        }]
    },
    {
        "algo_module": "aops_check.core.experiment.algorithm.single_item_check.nsigma.NSigma",
        "models": [{
            "model_id": "NSigma-1",
            "model_name": "NSigma",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": None,
            "precision": None
        }]
    },
    {
        "algo_module": "aops_check.core.experiment.algorithm.multi_item_check.statistical_multi_item_check."
                       "StatisticalCheck",
        "models": [{
            "model_id": "StatisticalCheck-1",
            "model_name": "StatisticalCheck",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": None,
            "precision": None
        }]
    },
    {
        "algo_module": "aops_check.core.experiment.algorithm.diag.statistics_diag.StatisticDiag",
        "models": [{
            "model_id": "StatisticDiag-1",
            "model_name": "StatisticDiag",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": None,
            "precision": None
        }]
    }
]


def init_algo_and_model():
    """
    add built in algorithm info into database
    """
    algo_proxy = AlgorithmDao()
    if not algo_proxy.connect(SESSION):
        LOGGER.error("Connect mysql fail when insert built-in algorithm.")
        raise sqlalchemy.exc.SQLAlchemyError("Connect mysql failed.")

    model_proxy = ModelDao()
    if not model_proxy.connect(SESSION):
        LOGGER.error("Connect mysql fail when insert built-in model.")
        raise sqlalchemy.exc.SQLAlchemyError("Connect mysql failed.")

    for algo in algo_list:
        module_path, class_name = algo["algo_module"].rsplit('.', 1)
        algo_module = import_module('.', module_path)
        class_ = getattr(algo_module, class_name)
        algo_info = deepcopy(class_().info)
        algo_id = str(uuid.uuid1()).replace('-', '')
        algo_info["algo_id"] = algo_id

        status_code = algo_proxy.insert_algo(algo_info)
        if status_code == DATABASE_INSERT_ERROR:
            LOGGER.error("Insert built-in algorithm '%s' into mysql failed." % algo_info["algo_name"])
            raise sqlalchemy.exc.SQLAlchemyError("Insert mysql failed.")

        model_list = algo["models"]
        for model_info in model_list:
            model_info["algo_id"] = algo_id
            status_code = model_proxy.insert_model(model_info)
            if status_code == DATABASE_INSERT_ERROR:
                LOGGER.error("Insert built-in model '%s' into mysql failed." % algo_info["model_name"])
                raise sqlalchemy.exc.SQLAlchemyError("Insert mysql failed.")

        LOGGER.info("Init built-in algorithm and model succeed.")
