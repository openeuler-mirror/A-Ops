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
from collections import defaultdict
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from elasticsearch import ElasticsearchException

from aops_utils.database.helper import sort_and_page
from aops_utils.database.proxy import ElasticsearchProxy, MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import (
    SUCCEED,
    DATABASE_INSERT_ERROR,
    DATABASE_QUERY_ERROR,
    NO_DATA,
    DATABASE_UPDATE_ERROR,
    DATABASE_DELETE_ERROR,
    DATA_EXIST)

from aops_check.database.factory.table import WorkflowHostAssociation, Workflow
from aops_check.conf.constant import WORKFLOW_INDEX


class WorkflowDao(MysqlProxy, ElasticsearchProxy):
    """
    Workflow related database operation
    """

    def __init__(self, configuration, host=None, port=None):
        """
        Instance initialization

        Args:
            configuration (Config)
            host(str)
            port(int)
        """
        MysqlProxy.__init__(self)
        ElasticsearchProxy.__init__(self, configuration, host, port)

    def connect(self, session):
        """
        connect to msyql and elasticsearch
        """
        return MysqlProxy.connect(self, session) and ElasticsearchProxy.connect(self)

    def insert_workflow(self, data: dict) -> int:
        """
        Insert workflow basic info into mysql and elasticsearch
        Args:
            data: parameter, e.g.
                {
                    "username": "admin",
                    "workflow_id": "id1",
                    "workflow_name": "workflow1",
                    "description": "a long description",
                    "status": "hold",
                    "app_name": "app1",
                    "app_id": "asd",
                    "input": {
                        "domain": "host_group_1",
                        "hosts": ["host_id1", "host_id2"]
                    },
                    "step": 5,
                    "period": 10,
                    "alert": {},
                    "detail": {
                        "singlecheck": {
                            "host_id1": {
                                "metric1": "3sigma"
                            }
                        },
                        "multicheck": {
                            "host_id1": "statistic"
                        },
                        "diag": "statistic"
                    },
                    "model_info": {
                        "model_id1": {
                            "model_name": "model name1",
                            "algo_name": "algo1",
                            "algo_id": "algo_id1"
                        }
                    }
                }
        Returns:
            int: status code
        """
        try:
            status_code = self._insert_workflow(data)
            self.session.commit()
            LOGGER.debug("Finished inserting new workflow.")
            return status_code
        except (SQLAlchemyError, ElasticsearchException) as error:
            self.session.rollback()
            LOGGER.error(error)
            LOGGER.error("Insert new workflow failed due to internal error.")
            return DATABASE_INSERT_ERROR

    def _insert_workflow(self, data: dict) -> int:
        """
        insert a workflow into database。
        1. insert workflow basic info into mysql workflow table
        2. isnert host workflow relationship into mysql workflow_host table
        3. insert workflow's detail and model info into elasticsearch
        Args:
            data: workflow info

        Returns:

        """
        workflow_name = data["workflow_name"]
        username = data["username"]

        if self._if_workflow_name_exists(workflow_name, username):
            LOGGER.debug("Insert workflow failed due to workflow name already exists.")
            return DATA_EXIST

        data.pop("alert")
        input_hosts = data.pop("input")
        hosts = input_hosts["hosts"]
        detail = data.pop("detail")
        model_info = data.pop("model_info")

        data["domain"] = input_hosts["domain"]

        # workflow table need commit after add, otherwise following insertion will fail due to
        # workflow.workflow_id foreign key constraint.
        workflow = Workflow(**data)
        self.session.add(workflow)
        self.session.commit()

        workflow_id = data["workflow_id"]
        try:
            self._insert_workflow_host_table(workflow_id, hosts)
            status_code = self._insert_workflow_into_es(username, workflow_id, detail, model_info)
            if status_code != SUCCEED:
                raise ElasticsearchException("Insert workflow '%s' in to elasticsearch failed."
                                             % workflow_id)

        except (SQLAlchemyError, ElasticsearchException):
            self.session.rollback()
            self.session.query(Workflow).filter(Workflow.workflow_id == workflow_id) \
                .delete()
            self.session.commit()
            raise
        return SUCCEED

    def _insert_workflow_host_table(self, workflow_id: str, hosts: list):
        """
        insert workflow and host's relationship into workflow_host_association table
        Args:
            workflow_id: workflow id
            hosts: host list

        """
        rows = [{"workflow_id": workflow_id, "host_id": host_id} for host_id in hosts]
        self.session.bulk_insert_mappings(WorkflowHostAssociation, rows)

    def _if_workflow_name_exists(self, workflow_name: str, username: str):
        """
        if the workflow name already exists in mysql
        Args:
            workflow_name: workflow name
            username: user name

        Returns:
            bool
        """
        workflow_count = self.session.query(func.count(Workflow.workflow_name)) \
            .filter(Workflow.workflow_name == workflow_name, Workflow.username == username).scalar()
        if workflow_count:
            return True
        return False

    def _insert_workflow_into_es(self, username: str, workflow_id: str, detail: dict,
                                 model_info: dict, index: Optional[str] = WORKFLOW_INDEX) -> int:
        """
        insert workflow's detail info and model info into elasticsearch
        """
        data = {
            "workflow_id": workflow_id,
            "username": username,
            "detail": detail,
            "model_info": model_info
        }
        res = ElasticsearchProxy.insert(self, index, data)
        if res:
            LOGGER.info("Add workflow '%s' info into es succeed.", workflow_id)
            return SUCCEED
        LOGGER.error("Add workflow '%s' info into es failed", workflow_id)
        return DATABASE_INSERT_ERROR

    def get_workflow_list(self, data: dict) -> Tuple[int, Dict]:
        """
        Get workflow list of a user

        Args:
            data(dict): parameter, e.g.
                {
                    "page": 1,
                    "per_page": 10,
                    "username": "admin",
                    "domain": "host_group1",
                    "status": "hold/running/recommending"
                }

        Returns:
            int: status code
            dict: query result. e.g.
                {
                    "total_count": 1,
                    "total_page": 1,
                    "workflows": [
                        {
                            "workflow_id": "123456",
                            "workflow_name": "workflow1",
                            "description": "a long description",
                            "status": "hold",
                            "app_name": "app1",
                            "app_id": "app_id",
                            "input": {
                                "domain": "host_group1",
                                "hosts": ["host_id1", "host_id2"]
                            }
                        }
                    ]
                }
        """
        result = {}
        try:
            result = self._get_workflow_list(data)
            self.session.commit()
            LOGGER.debug("Finished getting workflow list.")
            return SUCCEED, result
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Get workflow list failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_workflow_list(self, data: dict) -> Dict:
        """
        get workflow from database
        Args:
            data: query info

        Returns:
            dict: query result
        """
        result = {
            "total_count": 0,
            "total_page": 1,
            "result": []
        }

        workflow_query = self._query_workflow_list(data["username"], data.get("domain"),
                                                   data.get("status"))
        total_count = len(workflow_query.all())
        if not total_count:
            return result

        page, per_page = data.get('page'), data.get('per_page')
        processed_query, total_page = sort_and_page(workflow_query, None, None, per_page, page)

        workflow_id_list = [row.workflow_id for row in processed_query]
        workflow_host = self._get_workflow_hosts(workflow_id_list)
        result['result'] = self.__process_workflow_list_info(processed_query, workflow_host)
        result['total_page'] = total_page
        result['total_count'] = total_count
        return result

    def _query_workflow_list(self, username: str, domain: Optional[str],
                             status: Optional[str]) -> sqlalchemy.orm.query.Query:
        """
        query needed workflow basic info list
        Args:
            username: user name
            domain: host group name, could be none if not filtered
            status: status of workflow, could be none if not filtered

        Returns:
            sqlalchemy.orm.query.Query
        """
        filters = set()
        filters.add(Workflow.username == username)
        if domain:
            filters.add(Workflow.domain == domain)
        if status:
            filters.add(Workflow.status == status)

        workflow_query = self.session.query(Workflow.workflow_name, Workflow.workflow_id,
                                            Workflow.description, Workflow.status,
                                            Workflow.app_name, Workflow.app_id, Workflow.domain) \
            .filter(*filters)
        return workflow_query

    def _get_workflow_hosts(self, workflow_id_list: list) -> Dict:
        """
        get workflow host list
        Args:
            workflow_id_list: workflow id list

        Returns:
            dict: workflow's hosts, e.g.
                {
                    "workflow1": ["host_id1", "host_id2"]
                }
        """
        hosts_query = self.session.query(WorkflowHostAssociation.workflow_id,
                                         WorkflowHostAssociation.host_id) \
            .filter(WorkflowHostAssociation.workflow_id.in_(workflow_id_list))

        workflow_host = defaultdict(list)
        for row in hosts_query:
            workflow_host[row.workflow_id].append(row.host_id)

        return dict(workflow_host)

    @staticmethod
    def __process_workflow_list_info(workflow_info: sqlalchemy.orm.query.Query,
                                     workflow_host: dict) -> list:
        """
        combine workflow info and workflow's host together.
        In some abnormal circumstance, workflow may has no hosts, here we give empty host
        list to the workflow
        """
        result = []
        for row in workflow_info:
            workflow_info = {
                "workflow_name": row.workflow_name,
                "description": row.description,
                "status": row.status,
                "app_name": row.app_name,
                "app_id": row.app_id,
                "input": {
                    "domain": row.domain,
                    "hosts": workflow_host.get(row.workflow_id, [])
                },
                "workflow_id": row.workflow_id
            }
            result.append(workflow_info)
        return result

    def get_workflow(self, data) -> Tuple[int, dict]:
        """
        get workflow's detail info
        Args:
            data:  e.g. {"username": "admin", "workflow_id": ""}

        Returns:
            dict: workflow detail info  e.g.
                {
                    "workflow_id": "workflow_id1",
                    "workflow_name": "workflow_name1",
                    "description": "a long description",
                    "status": "running/hold/recommending",
                    "app_name": "app1",
                    "app_id": "app_id1",
                    "input": {
                        "domain": "host_group1",
                        "hosts": ["host_id1", "host_id2"]
                    },
                    "step": 5,
                    "period": 30,
                    "alert": {},
                    "detail": {
                        {
                            "singlecheck": {
                                "host_id1": {
                                    "metric1": "3sigma"
                                }
                            },
                            "multicheck": {
                                "host_id1": "statistic"
                            },
                            "diag": "statistic"
                        }
                    },
                    "model_info": {
                        "model_id1": {
                            "model_name": "model_name1",
                            "algo_id": "algo_id1",
                            "algo_name": "algo_name1"
                        }
                    }
                }
        """
        result = {}
        try:
            status_code, result = self._get_workflow_info(data)
            self.session.commit()
            LOGGER.debug("Finished getting workflow info.")
            return status_code, result
        except (SQLAlchemyError, ElasticsearchException) as error:
            LOGGER.error(error)
            LOGGER.error("Get workflow info failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_workflow_info(self, data) -> Tuple[int, dict]:
        """
        get workflow basic info from mysql and detail info from elasticsearch
        Args:
            data: e.g. {"username": "admin", "workflow_id": ""}

        Returns:
            int, dict
        """
        basic_info = self._get_workflow_basic_info(data["username"], data["workflow_id"])
        status_code, detail_info = self._get_workflow_detail_info(data)
        if status_code != SUCCEED:
            return status_code, {}

        basic_info.update(detail_info)
        return SUCCEED, {"result": basic_info}

    def _get_workflow_basic_info(self, username: str, workflow_id: str) -> dict:
        """
        get workflow basic info such as name, description, app_id... from mysql table
        Args:
            username: user name
            workflow_id: workflow id
        Returns:
            dict
        """
        filters = set()
        filters.add(Workflow.username == username)
        filters.add(Workflow.workflow_id == workflow_id)

        workflow_query = self.session.query(Workflow.workflow_name, Workflow.workflow_id,
                                            Workflow.description, Workflow.status,
                                            Workflow.app_name, Workflow.app_id, Workflow.domain) \
            .filter(*filters).one()

        workflow_host = self._get_workflow_hosts([workflow_id])

        workflow_info = {
            "workflow_name": workflow_query.workflow_name,
            "description": workflow_query.description,
            "status": workflow_query.status,
            "app_name": workflow_query.app_name,
            "app_id": workflow_query.app_id,
            "input": {
                "domain": workflow_query.domain,
                "hosts": workflow_host.get(workflow_query.workflow_id, [])
            },
            "workflow_id": workflow_query.workflow_id
        }
        return workflow_info

    def _get_workflow_detail_info(self, data, index: str = WORKFLOW_INDEX) -> Tuple[int, dict]:
        """
        Get workflow detail info from elasticsearch
        Args:
            data:  e.g. {"workflow_id": ""}
        Returns:
            dict:  e.g. {"detail": {}}
        """
        result = {}
        query_body = self._general_body(data)
        query_body["query"]["bool"]["must"].append(
            {"term": {"workflow_id": data["workflow_id"]}}
        )
        status, res = self.query(index, query_body)
        if status:
            if len(res['hits']['hits']) == 0:
                return NO_DATA, result
            LOGGER.debug("query workflow %s succeed", data['workflow_id'])
            result = res['hits']['hits'][0]['_source']
            return SUCCEED, result

        LOGGER.error("query workflow %s fail", data['workflow_id'])
        return DATABASE_QUERY_ERROR, result

    def update_workflow(self, data) -> int:
        """
        Update workflow
        Args:
            data: workflow's detail info.  e.g.
                {
                    "username": "admin",
                    "detail": {
                        {
                            "singlecheck": {
                                "host_id1": {
                                    "metric1": "3sigma"
                                }
                            },
                            "multicheck": {
                                "host_id1": "statistic"
                            },
                            "diag": "statistic"
                        }
                    }
                }

        Returns:

        """
        try:
            status_code = self._update_workflow(data)
            LOGGER.debug("Finished updating workflow detail info in elasticsearch.")
            return status_code
        except ElasticsearchException as error:
            LOGGER.error(error)
            LOGGER.error("Updating workflow detail info failed due to internal error.")
            return DATABASE_UPDATE_ERROR

    def _update_workflow(self, data: dict, index: str = WORKFLOW_INDEX) -> int:
        """
        update workflow's detail info in es
        """
        workflow_id = data["workflow_id"]
        action = [{
            "_id": workflow_id,
            "_source": data,
            "_index": index}]
        update_res = self._bulk(action)

        if not update_res:
            return DATABASE_UPDATE_ERROR
        return SUCCEED

    def delete_workflow(self, data: dict) -> int:
        """
        delete workflow by id
        Args:
            data (dict): parameter, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }

        Returns:
            int: status code
        """
        try:
            status_code = self._delete_workflow(data)
            self.session.commit()
            LOGGER.debug("Finished deleting workflow.")
            return status_code
        except (SQLAlchemyError, ElasticsearchException) as error:
            self.session.rollback()
            LOGGER.error(error)
            LOGGER.error("Deleting workflow failed due to internal error.")
            return DATABASE_DELETE_ERROR

    def _delete_workflow(self, data, index: str = WORKFLOW_INDEX) -> int:
        if self._if_workflow_running(data):
            return DATABASE_DELETE_ERROR

        filters = {Workflow.workflow_id == data["workflow_id"], Workflow.username == data["username"]}
        self.session.query(Workflow).filter(*filters).delete()

        query_body = self._general_body()
        query_body["query"]["bool"]["must"].extend(
            [{"term": {"username": data["username"]}}, {"term": {"workflow_id": data["workflow_id"]}}])

        res = ElasticsearchProxy.delete(self, index, query_body)
        if res:
            LOGGER.debug("Delete workflow from elasticsearch succeed.")
            return SUCCEED

        LOGGER.error("Delete workflow from elasticsearch failed due to internal error.")
        return DATABASE_DELETE_ERROR

    def _if_workflow_running(self, data) -> int:
        """
        check if workflow running or recommending
        """
        username = data["username"]
        workflow_id = data["workflow_id"]

        filters = {Workflow.username == username, Workflow.workflow_id == workflow_id}
        workflow_query = self.session.query(Workflow.status).filter(*filters).one()

        if workflow_query.status == "running" or workflow_query.status == "recommend":
            LOGGER.info("Delete workflow '%s' failed because it's still %s" % (workflow_id, workflow_query.status))
            return True
        return False

    def if_host_in_workflow(self, data: dict) -> Tuple[int, dict]:
        """
        if host exist workflow
        Args:
            data (dict): parameter, e.g.
                {
                    "username": "admin",
                    "host_list": ["host_id1", "host_id2"]
                }

        Returns:
            int: status code
            bool: if host exists or not:  {"host_id1": True, "host_id2": False}
        """
        result = {}
        try:
            result = self._query_host_in_workflow(data)
            LOGGER.debug("Query if a host exists in a workflow succeed.")
            return SUCCEED, result
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Query if a host exists in a workflow failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _query_host_in_workflow(self, data):
        host_query = self.session.query(WorkflowHostAssociation.host_id,
                                        func.count(WorkflowHostAssociation.workflow_id).label("workflow_num")) \
            .join(Workflow, Workflow.workflow_id == WorkflowHostAssociation.workflow_id) \
            .filter(WorkflowHostAssociation.host_id.in_(data["host_list"]),
                    Workflow.username == data["username"])

        result = {host_id: False for host_id in data["host_list"]}
        for row in host_query.all():
            if row.workflow_num:
                result[row.host_id] = True

        return result
