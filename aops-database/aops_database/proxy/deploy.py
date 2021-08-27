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
Description:
"""
import json

from aops_database.proxy.proxy import ElasticsearchProxy
from aops_database.conf.constant import TEMPLATE_INDEX, TASK_INDEX
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_DELETE_ERROR, DATABASE_INSERT_ERROR,\
    DATABASE_QUERY_ERROR, SUCCEED


class DeployDatabase(ElasticsearchProxy):
    """
    Database operation for deploy
    """

    def add_task(self, data):
        """
        Add task to index

        Args:
            data(dict): parameter, e.g.
                {
                    "task_id": "task1-121212",
                    "task_name": "task1",
                    "description": "it's good.",
                    "template_name": [],
                    "username": "admin"
                }
        Returns:
            int: status code
        """
        res = self.insert(TASK_INDEX, data)
        if res:
            LOGGER.info("add task [%s] succeed", data['task_name'])
            return SUCCEED
        LOGGER.error("add task [%s] fail", data['task_name'])
        return DATABASE_INSERT_ERROR

    def delete_task(self, data):
        """
        Delete task

        Args:
            data(dict): parameter, e.g.
                {
                    "task_list": ["task1", "task2"],
                    "username": "admin"
                }

        Returns:
            int: status code
        """
        task_list = data.get('task_list')

        body = self._general_body(data)
        body["query"]["bool"]["must"].append(
            {"terms": {"task_id": task_list}})
        res = self.delete(TASK_INDEX, body)
        if res:
            LOGGER.info("delete task %s succeed", task_list)
            return SUCCEED

        LOGGER.error("delete task %s fail", task_list)
        return DATABASE_DELETE_ERROR

    def get_task(self, data):
        """
        Get task

        Args:
            data(dict): parameter, e.g.
                {
                    "task_list": ["task1", "task2"],
                    "username": "admin",
                    "sort": "task_name
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

        query_body = self._general_body(data)

        task_list = data.get('task_list')
        if task_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"task_id": task_list}})
        count_res = self.count(TASK_INDEX, query_body)
        if not count_res[0]:
            LOGGER.error("query count of task fail")
            return DATABASE_QUERY_ERROR, result
        if count_res[1] == 0:
            LOGGER.info("there is no matched task")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)
        res = self.query(TASK_INDEX, query_body, [
            "task_id", "task_name", "description", "host_list", "template_name"])
        if res[0]:
            LOGGER.info("query task %s succeed", task_list)
            result["total_page"] = total_page
            result["total_count"] = total_count
            for item in res[1]['hits']['hits']:
                result["task_infos"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query task %s fail", task_list)
        return DATABASE_QUERY_ERROR, result

    def add_template(self, data):
        """
        Add template

        Args:
            data(dict): template info, e.g.
                {
                    "template_name": "a",
                    "template_content": {},
                    "description": "xxx,
                    "username": "admin"
                }

        Returns:
            int: status code
        """
        data['template_content'] = json.dumps(data['template_content'])
        res = self.insert(TEMPLATE_INDEX, data)
        if res:
            LOGGER.info("add template [%s] succeed", data.get('template_name'))
            return SUCCEED

        LOGGER.error("add template [%s] fail", data.get('template_name'))
        return DATABASE_INSERT_ERROR

    def get_template(self, data):
        """
        Get template

        Args:
            data(dict): parameter, e.g.
                {
                    "template_list": ["a"],
                    "username": "admin",
                    "sort": "template_name",
                    "direction": "asc",
                    "page": 1,
                    "per_page": 11
                }

        Returns:
            int: status code
            dict: query body
        """
        result = {
            "total_count": 0,
            "total_page": 0,
            "template_infos": []
        }

        query_body = self._general_body(data)

        template_list = data.get('template_list')
        if template_list:
            query_body["query"]["bool"]["must"].append(
                {"terms": {"template_name": template_list}})

        count_res = self.count(TEMPLATE_INDEX, query_body)
        if not count_res[0]:
            LOGGER.error("query count of template fail")
            return DATABASE_QUERY_ERROR, result
        if count_res[1] == 0:
            LOGGER.info("there is no matched template")
            return SUCCEED, result

        total_count = count_res[1]
        total_page = self._make_es_paginate_body(data, total_count, query_body)
        res = self.query(TEMPLATE_INDEX, query_body, [
                         "template_name", "template_content", "description"])
        if res[0]:
            LOGGER.info("query template %s succeed", template_list)
            result["total_page"] = total_page
            result["total_count"] = total_count
            for item in res[1]['hits']['hits']:
                item['_source']['template_content'] = json.loads(
                    item['_source']['template_content'])
                result["template_infos"].append(item['_source'])
            return SUCCEED, result

        LOGGER.error("query template %s fail", template_list)
        return DATABASE_QUERY_ERROR, result

    def delete_template(self, data):
        """
        Delete template

        Args:
            data(dict): parameter, e.g.
                {
                    "template_list": ["a"],
                    "username": "admin"
                }

        Returns:
            int: status code
        """
        template_list = data.get('template_list')

        body = self._general_body(data)
        body["query"]["bool"]["must"].append(
            {"terms": {"template_name": template_list}})
        res = self.delete(TEMPLATE_INDEX, body)
        if res:
            LOGGER.info("delete template %s succeed", template_list)
            return SUCCEED

        LOGGER.error("delete template %s fail", template_list)
        return DATABASE_DELETE_ERROR
