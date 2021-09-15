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
Description: Diag database operation
"""
import json

from aops_database.proxy.proxy import ElasticsearchProxy
from aops_database.conf.constant import DIAG_TASK_INDEX, DIAG_TREE_INDEX, DIAG_REPORT_INDEX
from aops_database.function.helper import judge_return_code
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_DELETE_ERROR, DATABASE_INSERT_ERROR,\
    DATABASE_QUERY_ERROR, SUCCEED


class DiagDatabase(ElasticsearchProxy):
    """
    Diag related es operation
    """

    def import_diag_tree(self, data):
        """
        Import diag tree

        Args:
            data(dict): e.g.
                {
                    "trees": [
                        {
                            "tree_name": "tree1",
                            "tree_content": {},
                            "description": "xx"
                        }
                    ],
                    "username": "admin"
                }

        Returns:
            int: status code
            dict
        """
        username = data['username']
        trees = data['trees']
        result = {
            "succeed_list": [],
            "fail_list": [],
            "update_list": []
        }
        query_body = self._general_body(data)
        query_body['query']['bool']['must'].append(
            {"match": {"tree_name": ""}})
        for tree in trees:
            # serialize
            tree['tree_content'] = json.dumps(tree['tree_content'])
            # query first, return true if need updated
            if self._update_diag_tree(tree, query_body, result):
                continue
            # insert
            tree['username'] = username
            self._add_diag_tree(tree, result)

        status_code = judge_return_code(result, DATABASE_INSERT_ERROR)
        return status_code, result

    def _update_diag_tree(self, data, query_body, result):
        """
        Update diag tree accoring to the tree name

        Args:
            data(dict): check item
            query_body(dict): query DSL
            result(dict): record

        Returns:
            bool: return True if need updated
        """
        tree_name = data.get('tree_name')
        query_body['query']['bool']['must'][1]["match"]["tree_name"] = tree_name
        res = self.query(DIAG_TREE_INDEX, query_body)
        if res[0] and len(res[1]['hits']['hits']) > 0:
            LOGGER.warning(
                "diag tree [%s] has existed, choose to update it", tree_name)
            _id = res[1]['hits']['hits'][0]['_id']
            action = [{"_id": _id, "doc": data}]
            res = self.update_bulk(DIAG_TREE_INDEX, action)
            if res:
                LOGGER.info("update diag tree [%s] succeed", tree_name)
                result['update_list'].append(tree_name)
            else:
                LOGGER.error("update diag tree [%s] fail", tree_name)
                result['fail_list'].append(tree_name)

            return True
        return False

    def _add_diag_tree(self, data, result):
        """
        Insert diag tree into database

        Args:
            check_item(dict): check item
            result(dict): record
        """
        tree_name = data.get("tree_name")
        res = self.insert(DIAG_TREE_INDEX, data)
        if res:
            LOGGER.info("insert diag tree [%s] succeed", tree_name)
            result['succeed_list'].append(tree_name)
        else:
            LOGGER.error("insert diag tree [%s] fail", tree_name)
            result['fail_list'].append(tree_name)

    def delete_diag_tree(self, data):
        """
        Delete diag tree

        Args:
            data(dict): e.g.
                {
                    "tree_list": ["tree1", "tree2"],
                    "username": "admin"
                }

        Returns:
            int: status code
        """
        tree_list = data.get('tree_list')

        body = self._general_body(data)
        body["query"]["bool"]["must"].append(
            {"terms": {"tree_name": tree_list}})
        res = self.delete(DIAG_TREE_INDEX, body)
        if res:
            LOGGER.info("delete fault diagnose tree %s succeed", tree_list)
            return SUCCEED

        LOGGER.error("delete fault diagnose tree %s fail", tree_list)
        return DATABASE_DELETE_ERROR

    def get_diag_tree(self, data):
        """
        Get diag tree

        Args:
            data(dict): e.g.
                {
                    "username": "admin"
                    "tree_list": ["tree1", "tree2"]
                }

        Returns:
            bool
        """
        result = {
            "trees": []
        }
        query_body = self._general_body(data)

        tree_list = data.get('tree_list')
        if tree_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"tree_name": tree_list}})
        res = self.scan(DIAG_TREE_INDEX, query_body, source=[
                        'tree_name', 'tree_content', 'description', 'tag'])
        if res[0]:
            LOGGER.info("query diag tree %s succeed", tree_list)
            # deserialize
            for tree in res[1]:
                tree['tree_content'] = json.loads(tree['tree_content'])
            result["trees"] = res[1]
            return SUCCEED, result

        LOGGER.error("query diag tree %s fail", tree_list)
        return DATABASE_QUERY_ERROR, result

    def save_diag_report(self, data):
        """
        Save diag report

        Args:
            data(dict): e.g.
                {
                    "reports": [
                        {
                            "username": "admin",
                            "host_id": "host1",
                            "tree_name": "name1",
                            "task_id": "task1",
                            "report_id": "xxxx",
                            "start": 11,
                            "end": 22,
                            "report": ""
                        }
                    ]
                }

        Returns:
            int: status code
        """
        reports = data.get('reports')
        res = self.insert_bulk(DIAG_REPORT_INDEX, reports)
        if res:
            LOGGER.info("save diag report succeed")
            return SUCCEED

        LOGGER.error("save diag report fail")
        return DATABASE_INSERT_ERROR

    def delete_diag_report(self, data):
        """
        Delete diag report

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "report_list": ["xx"]
                }

        Returns:
            int: status code
        """
        report_list = data.get('report_list')

        body = self._general_body(data)
        body["query"]["bool"]["must"].append(
            {"terms": {"report_id": report_list}})
        res = self.delete(DIAG_REPORT_INDEX, body)
        if res:
            LOGGER.info("delete diag report %s succeed", report_list)
            return SUCCEED

        LOGGER.error("delete diag report %s fail", report_list)
        return DATABASE_DELETE_ERROR

    def get_diag_report_list(self, data):
        """
        Get diag report list

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "time_range": [1, 3],
                    "host_list": ['id1', 'id2'],
                    "task_id": "task1",
                    "tree_list": ["tree1", "tree2"],
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
            "total_page": 0,
            "result": []
        }

        query_body = self._generate_query_report_body(data)
        count_res = self.count(DIAG_REPORT_INDEX, query_body)
        if not count_res[0]:
            LOGGER.error("query count of diag report fail")
            return DATABASE_QUERY_ERROR, result
        if count_res[1] == 0:
            LOGGER.info("there is no matched diag report")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)
        res = self.query(DIAG_REPORT_INDEX, query_body, [
            "host_id", "tree_name", "task_id", "report_id", "start", "end"])
        if res[0]:
            LOGGER.info("query diag report succeed")
            result["total_page"] = total_page
            result["total_count"] = total_count
            for item in res[1]['hits']['hits']:
                result["result"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query diag report fail")
        return DATABASE_QUERY_ERROR, result

    def _generate_query_report_body(self, data):
        """
        Generate query body

        Args:
            data(dict)

        Returns:
            query body
        """
        time_range = data.get('time_range')
        host_list = data.get('host_list')
        tree_list = data.get('tree_list')
        task_id = data.get('task_id')
        query_body = self._general_body(data)

        if task_id:
            query_body["query"]["bool"]["must"].append(
                {"match": {"task_id": task_id}})
        else:
            if host_list:
                query_body["query"]["bool"]["must"].append(
                    {"terms": {"host_id": host_list}})
            if tree_list:
                query_body["query"]["bool"]["must"].append(
                    {"terms": {"tree_name": tree_list}})
            if time_range and len(time_range) == 2:
                query_body["query"]["bool"]["must"].extend(
                    [{"range": {
                        "end": {"gte": time_range[0]}
                    }
                    },
                        {"range": {
                            "start": {"lte": time_range[1]}
                        }
                    }
                    ])
                query_body["query"]["bool"]["should"] = [
                    {"range": {
                        "end": {"lte": time_range[1]}
                    }
                    },
                    {"range": {
                        "start": {"gte": time_range[0]}
                    }
                    }
                ]

        return query_body

    def get_diag_report(self, data):
        """
        Get diag report

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "report_list": ["xxxx"]
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "result": []
        }
        report_list = data.get('report_list')

        query_body = self._general_body(data)
        query_body["query"]["bool"]["must"].append(
            {"terms": {"report_id": report_list}})

        res = self.query(DIAG_REPORT_INDEX, query_body, [
            "host_id", "tree_name", "task_id", "report_id", "start", "end", "report"])
        if res[0]:
            LOGGER.info("query report %s succeed", report_list)
            for item in res[1]['hits']['hits']:
                item['_source']['report'] = json.loads(
                    item['_source']['report'])
                result["result"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query report %s fail", report_list)
        return DATABASE_QUERY_ERROR, result

    def get_diag_process(self, data):
        """
        Get diag process

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "task_list": ["id1"]
                }

        Returns:
            int: status code
            dict: result
        """
        result = {
            "result": []
        }

        query_body = self._general_body(data)
        query_body["query"]["bool"]["must"].append({})

        task_list = data['task_list']
        if not task_list:
            return SUCCEED, result

        for task_id in task_list:
            query_body["query"]["bool"]["must"][1] = {
                "match": {"task_id": task_id}}
            count_res = self.count(DIAG_REPORT_INDEX, query_body)
            if not count_res[0]:
                result["result"].append({"task_id": task_id, "progress": 0})
            else:
                result["result"].append(
                    {"task_id": task_id, "progress": count_res[1]})

        return SUCCEED, result

    def save_diag_task(self, data):
        """
        Save diag task

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "task_id": "id",
                    "time": 111,
                    "host_list": [],
                    "tree_list": [],
                    "time_range": [],
                    "expected_report_num": 11
                }

        Returns:
            int: status code
        """
        res = self.insert(DIAG_TASK_INDEX, data)
        if res:
            LOGGER.info("save diag task succeed")
            return SUCCEED

        LOGGER.error("save diag task fail")
        return DATABASE_INSERT_ERROR

    def get_diag_task(self, data):
        """
        Get diag task list

        Args:
            data(dict): e.g.
                {
                    "username": "admin",
                    "time_range": [1, 2],
                    "task_list": [],
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
            "total_page": 0,
            "task_infos": []
        }

        query_body = self._generate_query_task_body(data)
        count_res = self.count(DIAG_TASK_INDEX, query_body)
        if not count_res[0]:
            LOGGER.error("query count of diag task fail")
            return DATABASE_QUERY_ERROR, result
        if count_res[1] == 0:
            LOGGER.info("there is no matched diag task")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)
        res = self.query(DIAG_TASK_INDEX, query_body, [
            "task_id", "host_list", "time_range", "time",
            "tree_list", "expected_report_num"])
        if res[0]:
            LOGGER.info("query diag task succeed")
            result["total_page"] = total_page
            result["total_count"] = total_count
            for item in res[1]['hits']['hits']:
                result["task_infos"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query diag task fail")
        return DATABASE_QUERY_ERROR, result

    def _generate_query_task_body(self, data):
        """
        Generate task query body

        Args:
            data(dict)

        Returns:
            query body
        """
        query_body = self._general_body(data)
        time_range = data.get('time_range')
        task_list = data.get('task_list')
        if task_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"task_id": task_list}})
        elif time_range and len(time_range) == 2:
            query_body["query"]["bool"]["must"].extend(
                [{"range": {
                    "time": {"gte": time_range[0]}
                }
                },
                    {"range": {
                        "time": {"lte": time_range[1]}
                    }
                }
                ])

        return query_body
