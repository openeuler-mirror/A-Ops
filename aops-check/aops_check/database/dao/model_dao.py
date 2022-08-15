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
from typing import Tuple, Dict, List, Optional

from aops_utils.database.helper import judge_return_code
from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_QUERY_ERROR, NO_DATA, DATABASE_INSERT_ERROR, DATA_EXIST
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from aops_check.database.factory.table import Model, Algorithm


class ModelDao(MysqlProxy):
    """
    Model related operation
    """

    def insert_model(self, data) -> int:
        """
        insert model info into database
        Args:
            data: e.g. {
                "model_id": "model_id1",
                "model_name": "model_name1",
                "tag": "biga_data,web",
                "algo_id": "",
                "create_time": "",
                "file_path": "",
                "precision": "0.8"
            }

        Returns:
            int
        """
        try:
            status_code = self._insert_model(data)
            LOGGER.debug("Finished inserting model's info.")
            return status_code
        except (SQLAlchemyError, KeyError) as error:
            LOGGER.error(error)
            LOGGER.error("Insert model's info failed due to internal error.")
            return DATABASE_INSERT_ERROR

    def _insert_model(self, data):
        if self._if_model_exists(data.get("username", None), data["model_name"], data["file_path"]):
            return DATA_EXIST

        model = Model(**data)
        self.session.add(model)
        self.session.commit()
        return True

    def _if_model_exists(self, username: Optional[str], model_name: str, file_path: Optional[str]) -> bool:
        """
        if the model name already exists in mysql and file path exist or not
        Args:
            model_name: model name
            username: user name
            file_path: model file's path

        Returns:
            bool
        """
        name_count = self.session.query(func.count(Model.model_name)) \
            .filter(Model.model_name == model_name, Model.username == username).scalar()
        if name_count:
            return True

        if not file_path:
            return False

        file_count = self.session.query(func.count(Model.file_path)) \
            .filter(Model.file_path == file_path, Model.username == username).scalar()
        if file_count:
            return True
        return False

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
