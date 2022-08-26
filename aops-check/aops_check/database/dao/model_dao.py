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
from typing import Tuple, Dict, List
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from aops_utils.database.helper import judge_return_code, sort_and_page
from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import SUCCEED, DATABASE_QUERY_ERROR, NO_DATA, \
    DATABASE_INSERT_ERROR, DATA_EXIST

from aops_check.conf.constant import SYSTEM_USER
from aops_check.database.factory.table import Model, Algorithm


class ModelDao(MysqlProxy):
    """
    Model related operation
    """

    def insert_model(self, data) -> int:
        """
        insert model info into database. Called after model's file has been saved.
        Args:
            data: e.g. {
                "username": "admin"
                "model_id": "model_id1",
                "model_name": "model_name1",
                "tag": "big_data,web",
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
        if self._if_model_exists(data["username"], data["model_name"]):
            return DATA_EXIST

        model = Model(**data)
        self.session.add(model)
        self.session.commit()
        return SUCCEED

    def _if_model_exists(self, username: str, model_name: str) -> bool:
        """
        if the model name already exists in mysql and file path exist or not
        Args:
            model_name: model name
            username: user name

        Returns:
            bool
        """
        name_count = self.session.query(func.count(Model.model_name)) \
            .filter(Model.model_name == model_name, Model.username.in_([username, SYSTEM_USER])) \
            .scalar()
        if name_count:
            return True
        return False

    def get_model_list(self, data: dict) -> Tuple[int, dict]:
        """
        get model info from database.
        Args:
            data: e.g. {
                "username": "admin",
                "page": 2,
                "per_page": 50,
                "sort": "precision",  // sort based on precision of model
                "direction": "asc",  // asc or desc
                "filter": {
                    "tag": "big_data",
                    "field": "single_check",
                    "model_name": "model1",
                    "algo_name": ["algo1", "algo2"]
                }
            }

        Returns:
            int
            dict: model list info.  e.g.
                {
                    "total_count": 0,
                    "total_page": 0,
                    "result": [{
                        "model_name": "model1",
                        "algo_name": "algo1",
                        "create_time": 12345678,
                        "precision": 0.8,
                        "tag": "big_data",
                        "model_id": "id1"
                    }]
                }
        """
        result = {}
        try:
            result = self._get_model_list(data)
            LOGGER.debug("Finished getting model list.")
            return SUCCEED, result
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Get model list failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_model_list(self, data: dict) -> dict:
        """
        get model list from mysql
        """
        result = {
            "total_count": 0,
            "total_page": 0,
            "result": []
        }

        filters = self._get_model_list_filters(
            data["username"], data.get("filter"))
        model_query = self._query_model_list(filters)

        total_count = len(model_query.all())
        if not total_count:
            return result

        direction, page, per_page = data.get(
            'direction'), data.get('page'), data.get('per_page')
        if data.get("sort"):
            sort_column = getattr(Model, data["sort"])
        else:
            sort_column = None
        processed_query, total_page = sort_and_page(model_query, sort_column,
                                                    direction, per_page, page)

        result['result'] = self._model_list_row2dict(processed_query)
        result['total_page'] = total_page
        result['total_count'] = total_count

        return result

    def _query_model_list(self, filters):
        """
        query needed model info
        Args:
            filters (set): filter given by user

        Returns:
            sqlalchemy.orm.query.Query
        """
        model_query = self.session.query(Model.model_name, Algorithm.algo_name, Model.create_time,
                                         Model.precision, Model.tag, Model.model_id) \
            .join(Algorithm, Model.algo_id == Algorithm.algo_id) \
            .filter(*filters)

        return model_query

    @staticmethod
    def _get_model_list_filters(username, filter_dict):
        """
        Generate filters

        Args:
            username (str): username
            filter_dict(dict): filter dict to filter model list, e.g.
                {
                    "tag": "big_data",
                    "field": "single_check",
                    "model_name": "model1",
                    "algo_name": ["algo1", "algo2"]
                }

        Returns:
            set
        """
        filters = {Model.username.in_([username, SYSTEM_USER])}
        if not filter_dict:
            return filters

        if filter_dict.get("model_name"):
            filters.add(Model.model_name.like(
                "%" + filter_dict["model_name"] + "%"))
        if filter_dict.get("algo_name"):
            filters.add(Algorithm.algo_name.in_(filter_dict["algo_name"]))
        if filter_dict.get("tag"):
            filters.add(Model.tag.like("%" + filter_dict["tag"] + "%"))
        if filter_dict.get("field"):
            filters.add(Algorithm.field == filter_dict["field"])

        return filters

    @staticmethod
    def _model_list_row2dict(rows):
        """
        reformat queried rows to list of dict
        """
        result = []
        for row in rows:
            model_info = {
                "model_name": row.model_name,
                "algo_name": row.algo_name,
                "create_time": row.create_time,
                "precision": row.precision,
                "tag": row.tag,
                "model_id": row.model_id
            }
            result.append(model_info)
        return result

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
            LOGGER.error(
                "Get model's algorithm info failed due to internal error.")
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
            LOGGER.debug(
                "No data found when getting the info of model: %s." % fail_str)

        status_dict = {"succeed_list": succeed_list, "fail_list": fail_list}
        status_code = judge_return_code(status_dict, NO_DATA)

        return status_code, result

    # builtin interface
    def get_model(self, model_list: List[str]) -> Tuple[int, Dict[str, dict]]:
        """
        The interface is for model loading, offering model path and algorithm path.
        """
        result = {}
        try:
            status_code, result = self._get_model_info(model_list)
            LOGGER.debug("Finished getting model's algorithm info.")
            return status_code, result
        except SQLAlchemyError:
            LOGGER.error("Get model info failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_model_info(self, model_list: List[str]) -> Tuple[int, Dict[str, dict]]:
        model_query = self.session.query(Model.model_id, Model.model_name, Model.file_path, Algorithm.path) \
            .join(Algorithm, Model.algo_id == Algorithm.algo_id) \
            .filter(Model.model_id.in_(model_list))

        result = {}
        for row in model_query:
            result[row.model_id] = {
                "model_path": row.file_path, "algo_path": row.path}

        succeed_list = list(result.keys())
        fail_list = list(set(model_list) - set(succeed_list))
        if fail_list:
            LOGGER.error(
                "No data found when getting the info of model: %s" % fail_list)

        status_dict = {"succeed_list": succeed_list, "fail_list": fail_list}
        status_code = judge_return_code(status_dict, NO_DATA)

        return status_code, result
