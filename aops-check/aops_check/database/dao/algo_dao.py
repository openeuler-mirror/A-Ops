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
from typing import Tuple, Dict

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from aops_utils.database.helper import sort_and_page
from aops_utils.restful.status import SUCCEED, DATABASE_QUERY_ERROR, NO_DATA
from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_INSERT_ERROR, DATA_EXIST
from aops_check.database.factory.table import Algorithm
from aops_check.conf.constant import SYSTEM_USER


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
        if self._if_algo_exists(data.get("username"), data["algo_name"]):
            return DATA_EXIST

        algo = Algorithm(**data)
        self.session.add(algo)
        return SUCCEED

    def _if_algo_exists(self, username: str, algo_name: str) -> bool:
        """
        if the algorithm name already exists in mysql or not
        Args:
            username: user name
            algo_name: model name

        Returns:
            bool
        """
        name_count = self.session.query(func.count(Algorithm.algo_name)) \
            .filter(Algorithm.algo_name == algo_name, Algorithm.username.in_([username, SYSTEM_USER])) \
            .scalar()
        if name_count:
            return True
        return False

    def query_algorithm_list(self, data) -> Tuple[int, dict]:
        """
            get algorithm list
        Args:
            data(dict): parameter, e.g.
                    {
                        'page': 1,
                        'per_page': 10,
                        'field': single,
                        'username': admin
                    }

        Returns:
            int: status code
            dict: query result

        Notes:
            If you do not enter anything, query all data by default.
        """
        page = data.get('page')
        per_page = data.get('per_page')
        filters = {Algorithm.username.in_([data.get('username'), 'system'])}
        if data.get('field'):
            filters.add(Algorithm.field == data.get('field'))

        res = {
            'total_count': 0,
            'total_page': 0,
            'algo_list': []
        }
        algo_query = self._query_algo_list(filters)
        total_count = len(algo_query.all())
        algo_info_list, total_page = sort_and_page(algo_query, None, None, per_page, page)
        res['algo_list'] = self._algo_rows_to_dict(algo_info_list)
        res['total_page'] = total_page
        res['total_count'] = total_count

        return SUCCEED, res

    def _query_algo_list(self, filters):
        """
            query needed algo info
        Args:
            filters (set): filter given by user

        Returns:
            sqlalchemy.orm.query.Query
        """
        return self.session.query(Algorithm.algo_id, Algorithm.algo_name, Algorithm.field,
                                  Algorithm.description).filter(*filters)

    @staticmethod
    def _algo_rows_to_dict(rows):
        """
            turn queried rows to list of dict
        """
        res = []
        for row in rows:
            algo_info = {
                "algo_id": row.algo_id,
                "algo_name": row.algo_name,
                "field": row.field,
                "description": row.description
            }
            res.append(algo_info)
        return res

    def query_algorithm(self, data: Dict[str, str]) -> Tuple[int, dict]:
        """
            query algorithm info from database

        Args:
            data(dict):
                {
                'algo_id':string,
                'username': admin
                }

        Returns:
            int: status code
            dict: query result
        """
        res = {"result": {}}
        try:
            algo_info = self.session.query(Algorithm).filter(
                Algorithm.algo_id == data['algo_id']).all()
            self.session.commit()
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Query algorithm basic info fail.")
            return DATABASE_QUERY_ERROR, {}

        if len(algo_info) == 0:
            return NO_DATA, res

        algo_info = algo_info[0]
        res = {
            "result": {
                "algo_id": data['algo_id'],
                "algo_name": algo_info.algo_name,
                "field": algo_info.field,
                "description": algo_info.description
            }
        }

        return SUCCEED, res
