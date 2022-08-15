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
from typing import Optional
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_INSERT_ERROR, DATA_EXIST
from aops_check.database.factory.table import Algorithm


class AlgorithmDao(MysqlProxy):
    """
    Algorithm related operation
    """
    def insert_algo(self, data) -> int:
        """
        insert algorithm info into database
        Args:
            data: e.g. {
                "username": "admin",  # empty string for built-in algorithm
                "algo_id": "id1",
                "algo_name": "name1",
                "field": "",
                "description": "a long description"
            }

        Returns:
            int
        """
        try:
            status_code = self._insert_algo(data)
            LOGGER.debug("Finished inserting algorithm info into mysql.")
            self.session.commit()
            return status_code
        except (SQLAlchemyError, KeyError) as error:
            LOGGER.error(error)
            LOGGER.error("Insert algorithm info failed due to internal error.")
            return DATABASE_INSERT_ERROR

    def _insert_algo(self, data):
        if self._if_algo_exists(data.get("username", None), data["algo_name"]):
            return DATA_EXIST

        algo = Algorithm(**data)
        self.session.add(algo)
        return True

    def _if_algo_exists(self, username: Optional[str], algo_name: str) -> bool:
        """
        if the algorithm name already exists in mysql or not
        Args:
            username: user name
            algo_name: model name

        Returns:
            bool
        """
        name_count = self.session.query(func.count(Algorithm.algo_name)) \
            .filter(Algorithm.algo_name == algo_name, Algorithm.username == username).scalar()
        if name_count:
            return True
        return False
