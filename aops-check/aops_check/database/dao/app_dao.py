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
from typing import Dict, Optional, Tuple

from aops_utils.database.proxy import ElasticsearchProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import (
    SUCCEED,
    DATABASE_INSERT_ERROR,
    DATABASE_QUERY_ERROR,
    NO_DATA,
    DATA_EXIST
)

from aops_check.conf.constant import APP_INDEX


class AppDao(ElasticsearchProxy):
    """
    It's a dao of app.
    """

    def __is_app_exists(self, username: str, app_name: str, index: str) -> bool:
        """
        Judge whether app has existed, the judge rule is that app's name of the user is same.
        """
        query_body = self._general_body()
        query_body["query"]["bool"]["must"].extend([
            {"term": {"username": username}},
            {'term': {'app_name': app_name}}])
        status, res = self.query(index, query_body, ['app_id'])
        if status and len(res['hits']['hits']) > 0:
            return True

        return False

    def create_app(self, data: Dict, index: Optional[str] = APP_INDEX) -> int:
        """
        Insert app info to elasticsearch.

        Args:
            data: app info, e.g.
                {
                    "username": "admin",
                    "app_name": "",
                    "app_id": "",
                    "version": "",
                    "api": {
                        "api": "",
                        "address": ""
                    },
                    "detail": {}
                }
            index: app index in elasticsearch
        """
        if self.__is_app_exists(data['username'], data['app_name'], index):
            return DATA_EXIST

        res = self.insert(index, data)
        if res:
            LOGGER.info("add app [%s] succeed", data['app_name'])
            return SUCCEED
        LOGGER.error("add app [%s] fail", data['app_name'])
        return DATABASE_INSERT_ERROR

    def query_app_list(self, data: Dict, index: Optional[str] = APP_INDEX) -> Tuple[int, Dict]:
        """
        Only return app min info, just for list display.

        Args:
            data: query args, e.g.
                {
                    "username": "admin",
                    "page": 1,
                    "per_page": 2
                }
            index: app index in elasticsearch
        """
        result = {
            "total_count": 0,
            "total_page": 0,
            "app_list": []
        }
        query_body = self._general_body(data)
        # return (succeed or fail: bool, count: int)
        count_res = self.count(index, query_body)
        if not count_res[0]:
            LOGGER.error("query app fail")
            return DATABASE_QUERY_ERROR, result

        if count_res[1] == 0:
            LOGGER.warning("there is no matched app")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)
        res = self.query(index, query_body, [
            "app_id", "version", "app_name", "description"])
        if res[0]:
            LOGGER.debug("query app list succeed")
            result["total_page"] = total_page
            result["total_count"] = total_count
            for item in res[1]['hits']['hits']:
                result["app_list"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query app list fail")
        return DATABASE_QUERY_ERROR, result

    def query_app(self, data: Dict, index: Optional[str] = APP_INDEX) -> Tuple[int, Dict]:
        """
        Query app specific info.

        Args:
            data: query args, e.g.
                {
                    "username": "admin",
                    "app_id": ""
                }
            index: app index in elasticsearch
        """
        result = {}
        query_body = self._general_body(data)
        query_body["query"]["bool"]["must"].append(
            {"term": {"app_id": data["app_id"]}}
        )
        status, res = self.query(index, query_body)
        if status:
            if len(res['hits']['hits']) == 0:
                return NO_DATA, result
            LOGGER.debug("query app %s succeed", data['app_id'])
            result['result'] = res['hits']['hits'][0]['_source']
            return SUCCEED, result

        LOGGER.error("query app %s fail", data['app_id'])
        return DATABASE_QUERY_ERROR, result
