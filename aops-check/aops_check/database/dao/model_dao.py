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
from typing import Tuple
from sqlalchemy.exc import SQLAlchemyError

from aops_utils.database.helper import judge_return_code
from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_QUERY_ERROR, NO_DATA
from aops_check.database.factory.table import Model, Algorithm


class ModelDao(MysqlProxy):
    """
    Model related operation
    """

    def get_model_algo(self, data: dict) -> Tuple[int, dict]:
        """
        get model's name and its algorithm info
        Args:
            data: e.g. {"model_list" : []}

        Returns:
            int, dict
        """
        result = {}
        try:
            status_code, result = self._get_model_algo_info(data["model_list"])
            LOGGER.debug("Finished getting model's algorithm info.")
            return status_code, result
        except (SQLAlchemyError, KeyError) as error:
            LOGGER.error(error)
            LOGGER.error("Get model's algorithm info failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_model_algo_info(self, model_list: list) -> Tuple[int, dict]:
        """
        get model's name and its algorithm info from mysql
        """
        model_query = self.session.query(Model.model_id, Model.model_name,
                                          Algorithm.algo_id, Algorithm.algo_name) \
            .join(Algorithm, Model.algo_id == Algorithm.algo_id) \
            .filter(Model.model_id.in_(model_list))

        result = {}
        for row in model_query:
            result[row.model_id] = {"model_name": row.model_name, "algo_id": row.algo_id,
                                     "algo_name": row.algo_name}

        succeed_list = list(result.keys())
        fail_list = list(set(model_list) - set(succeed_list))
        if fail_list:
            fail_str = ",".join(fail_list)
            LOGGER.debug("No data found when getting the info of model: %s." % fail_str)

        status_dict = {"succeed_list": succeed_list, "fail_list": fail_list}
        status_code = judge_return_code(status_dict, NO_DATA)

        return status_code, result
