#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description: Check database operation
"""
import math

from aops_database.proxy.proxy import ElasticsearchProxy
from aops_database.conf.constant import CHECK_RULE_INDEX, CHECK_RESULT_INDEX
from aops_database.function.helper import judge_return_code
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_DELETE_ERROR, DATABASE_INSERT_ERROR,\
    DATABASE_QUERY_ERROR, SUCCEED


class CheckDatabase(ElasticsearchProxy):
    """
    Check related es operation
    """

    def add_check_rule(self, data):
        """
        Add check rule

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "check_items: [
                        {
                            "check_item": "",
                            "data_list": [],
                            "condition": "",
                            "description": "",
                            "plugin": ""
                        }
                    ]
                }

        Returns:
            int: status code
            dict
        """
        username = data['username']
        check_items = data['check_items']
        result = {
            "succeed_list": [],
            "fail_list": []
        }
        record = set()
        query_body = self._general_body(data)
        query_body['query']['bool']['must'].append(
            {"match": {"check_item": ""}})
        for check_item in check_items:
            item_name = check_item.get('check_item')
            if item_name in record:
                LOGGER.warning("check rule [%s] has existed", item_name)
                continue
            # query first
            query_body['query']['bool']['must'][1]["match"]["check_item"] = item_name
            res = self.query(CHECK_RULE_INDEX, query_body)
            if res[0] and len(res[1]['hits']['hits']) > 0:
                LOGGER.warning("check rule [%s] has existed", item_name)
                continue
            check_item['username'] = username
            res = self.insert(CHECK_RULE_INDEX, check_item)
            if res:
                LOGGER.info("insert check rule [%s] succeed", item_name)
                result['succeed_list'].append(item_name)
                record.add(item_name)
            else:
                LOGGER.error("insert check rule [%s] fail", item_name)
                result['fail_list'].append(item_name)

        status_code = judge_return_code(result, DATABASE_INSERT_ERROR)
        return status_code, result

    def delete_check_rule(self, data):
        """
        Delete check rule

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "check_items": ["item1", "item2"]
                }

        Returns:
            int: status code
        """
        check_items = data.get('check_items')
        body = self._general_body(data)
        body["query"]["bool"]["must"].append(
            {"terms": {"check_item": check_items}})

        res = self.delete(CHECK_RULE_INDEX, body)
        if res:
            LOGGER.info("delete check rule %s succeed", check_items)
            return SUCCEED

        LOGGER.error("delete check rule %s fail", check_items)
        return DATABASE_DELETE_ERROR

    def get_check_rule(self, data):
        """
        Get check rule

        Args:
            data(dict): e.g.
                {
                    "username": "admin"
                    "check_items": ["item1", "item2"],
                    "sort": "tree_name",
                    "direction": "asc",
                    "page": 1,
                    "per_page": 11
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "total_count": 0,
            "check_items": [],
            "total_page": 0,
        }
        query_body = self._generate_query_rule_body(data)
        status_code, total_count = self._get_rule_count(query_body)
        if status_code != SUCCEED or total_count == 0:
            return status_code, result

        total_page = self._make_es_paginate_body(data, total_count, query_body)

        res = self.query(CHECK_RULE_INDEX, query_body, [
            'check_item', 'data_list', 'condition', 'description', 'plugin'])
        if res[0]:
            LOGGER.info("query check rule succeed")
            result["total_count"] = total_count
            result["total_page"] = total_page
            for item in res[1]['hits']['hits']:
                result["check_items"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query check rule fail")
        return DATABASE_QUERY_ERROR, result

    def get_rule_count(self, data):
        """
        Get check rule count

        Args:
            data(dict): e.g.
                {
                    "username": "admin"
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "rule_count": 0
        }
        query_body = self._generate_query_rule_body(data)
        status_code, total_count = self._get_rule_count(query_body)
        if total_count == 0:
            LOGGER.warning("there is no matched check items")
        result["rule_count"] = total_count
        return status_code, result

    def _generate_query_rule_body(self, data):
        """
        Generate check rule query body

        Args:
            data(dict)

        Returns:
            dict: query body
        """
        query_body = self._general_body(data)

        check_items = data.get('check_items')
        if check_items:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"check_item": check_items}})

        return query_body

    def _get_rule_count(self, body):
        """
        Get check rule count

        Args:
            body(dict): query body

        Returns:
            int: status code
            int: result
        """
        count_res = self.count(CHECK_RULE_INDEX, body)
        if not count_res[0]:
            LOGGER.error("query count of check rule fail")
            return DATABASE_QUERY_ERROR, 0

        return SUCCEED, count_res[1]

    def save_check_result(self, data):
        """
        Save check result

        Args:
            data(dict): e.g.
                {
                    "check_results": [
                        {
                            "username": "admin"
                            "host_id": "host1",
                            "data_list": ["data1", "data2"],
                            "start": 1,
                            "end": 2,
                            "check_item": "item1",
                            "condition": "sxx",
                            "value": "xx"
                        }
                    ]
                }

        Returns:
            int: status code
        """
        just_insert, need_update = self._split_results(data)
        if all([self.insert_bulk(CHECK_RESULT_INDEX, just_insert),
                self.update_bulk(CHECK_RESULT_INDEX, need_update)]):
            LOGGER.info("save or update check result succeed")
            return SUCCEED

        LOGGER.error("save or update check result fail")
        return DATABASE_INSERT_ERROR

    def _split_results(self, data):
        """
        Judge whether the result needs to be inserted or updated

        Args:
            data(dict)

        Returns:
            list: data that need inserted
            list: data that need updated
        """
        check_results = data.get("check_results")
        just_insert = []
        need_update = []
        for check_result in check_results:
            query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"username": check_result['username']}},
                            {"match": {"host_id": check_result['host_id']}},
                            {"match": {
                                "check_item": check_result['check_item']}},
                            {"match": {"start": check_result['start']}},
                            {"match": {"end": check_result['end']}}
                        ]
                    }
                }
            }
            res = self.query(CHECK_RESULT_INDEX, query_body)
            if res[0] and len(res[1]['hits']['hits']) != 0:
                LOGGER.info("query check result succeed")
                doc = {
                    "value": check_result["value"]
                }
                _id = res[1]['hits']['hits'][0]['_id']
                need_update.append({"_id": _id, "doc": doc})
            else:
                just_insert.append(check_result)
        return just_insert, need_update

    def delete_check_result(self, data):
        """
        Delete check result

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "host_list": ["id1", "id2"],
                    "time_range": [111, 222]
                }

        Returns:
            int: status code
        """
        body = self._generate_delete_result_body(data)
        res = self.delete(CHECK_RESULT_INDEX, body)
        if res:
            LOGGER.info("delete check result succeed")
            return SUCCEED

        LOGGER.error("delete check result fail")
        return DATABASE_DELETE_ERROR

    def _generate_delete_result_body(self, data):
        """
        Generate query body

        Args:
            data(dict)

        Returns:
            dict: query body
        """
        host_list = data.get('host_list')
        time_range = data.get('time_range')
        query_body = self._general_body(data)

        if host_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"host_id": host_list}})
        if time_range and len(time_range) == 2:
            query_body["query"]["bool"]["must"].extend(
                [{"range": {
                    "start": {"gte": time_range[0]}
                }
                },
                    {"range": {
                        "end": {"lte": time_range[1]}
                    }
                }
                ])

        return query_body

    def get_check_result(self, data):
        """
        Get check result

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "time_range": [1, 3],
                    "host_list": ['id1', 'id2'],
                    "check_items": ["item1"],
                    "sort": "check_item",
                    "direction": "asc",
                    "page": 1,
                    "per_page": 11
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "total_page": 0,
            "total_count": 0,
            "check_result": []
        }

        query_body = self._generate_query_result_body(data)
        count_res = self.count(CHECK_RESULT_INDEX, query_body)
        if not count_res[0]:
            LOGGER.error("query count of check result fail")
            return DATABASE_QUERY_ERROR, result
        if count_res[1] == 0:
            LOGGER.info("there is no matched check result")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)

        res = self.query(CHECK_RESULT_INDEX, query_body, [
            'check_item', 'data_list', 'condition',
            'value', 'host_id', 'start', 'end'])
        if res[0]:
            LOGGER.info("query check result succeed")
            result["total_count"] = total_count
            result["total_page"] = total_page

            for item in res[1]['hits']['hits']:
                result["check_result"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query check result fail")
        return DATABASE_QUERY_ERROR, result

    def _generate_query_result_body(self, data):
        """
        Generate query body

        Args:
            data(dict)

        Returns:
            dict: query body
        """
        host_list = data.get('host_list')
        time_range = data.get('time_range')
        check_items = data.get('check_items')
        query_body = self._general_body(data)

        if host_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"host_id": host_list}})
        if check_items:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"check_item": check_items}})
        if time_range and len(time_range) == 2:
            query_body["query"]["bool"]["must"].extend(
                [{"range": {
                    "start": {"lte": time_range[1]}
                }
                },
                    {"range": {
                     "end": {"gte": time_range[0]}
                     }
                     }
                ])
            query_body["query"]["bool"]["should"] = [
                {"range": {
                    "start": {"gte": time_range[0]}
                }
                },
                {"range": {
                    "end": {"lte": time_range[1]}
                }
                }
            ]

        return query_body

    def get_check_result_count(self, data):
        """
        Get check result count

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "host_list": ['id1', 'id2'],
                    "sort": "count",
                    "direction": "asc",
                    "page": 1,
                    "per_page": 11
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "results": [],
            "total_count": 0,
            "total_page": 0,
        }

        query_body = self._generate_count_body(data)
        res = self.query(CHECK_RESULT_INDEX, query_body)
        if res[0]:
            LOGGER.info("query check result succeed")
            total_count = len(res[1]['aggregations']['count']['buckets'])
            page = data.get('page')
            per_page = data.get("per_page")
            start = 0
            end = total_count
            total_page = 1
            if page and per_page:
                total_page = math.ceil(total_count / per_page)
                start = (page - 1) * per_page
                end = min(start + per_page, total_count)
            buckets = res[1]['aggregations']['count']['buckets'][start:end]
            for bucket in buckets:
                result['results'].append(
                    {"host_id": bucket['key'], "count": bucket['doc_count']})
            result['total_count'] = total_count
            result['total_page'] = total_page
            return SUCCEED, result

        LOGGER.error("query check result fail")
        return DATABASE_QUERY_ERROR, result

    def _generate_count_body(self, data):
        """
        Generate result count body

        Args:
            data(dict)

        Returns:
            dict: query body
        """
        query_body = self._general_body(data)

        host_list = data.get('host_list')
        if host_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"host_id": host_list}})
        # do not return all data
        query_body["size"] = 0
        # aggregate by host id
        query_body["aggs"] = {"count": {"terms": {"field": "host_id"}}}

        sort = data.get('sort')
        direction = data.get('direction') or 'asc'
        if sort and direction:
            if sort == 'count':
                query_body["aggs"]["count"]["terms"]["order"] = {
                    "_count": direction}
            if sort == 'host_id':
                query_body["aggs"]["count"]["terms"]["order"] = {
                    "_key": direction}

        return query_body
