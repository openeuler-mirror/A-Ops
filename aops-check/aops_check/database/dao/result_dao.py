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
from typing import Dict, Tuple, List, Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from aops_check.database.factory.table import HostCheckResult, AlertHost, DomainCheckResult
from aops_utils.database.helper import sort_and_page
from aops_utils.database.proxy import MysqlProxy
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_QUERY_ERROR, SUCCEED, NO_DATA


class ResultDao(MysqlProxy):
    def query_result_host(self, data: Dict[str, str]) -> Tuple[int, dict]:
        """
            query check result info from database

        Args:
            data(dict): parameter, e.g.
                {
                    "alert_id": "xxxx",
                    "username": "xxxx
                }

        Returns:
            int: status code
            dict:   e.g {
                        "result": {
                        "host id": {
                        "host_ip": "ip address",
                        "host_name": "string",
                        "is_root": false
                        "host_check_result":[{
                                "is_root": boolean,
                                "label": "string",
                                "metric_name": "string",
                                "time": time
                            }
                        ...
                        ]}}
        """
        res = {}

        try:
            check_result_info_list = self._query_check_host_info(data)
            self.session.commit()
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Query check result fail.")
            return DATABASE_QUERY_ERROR, res

        if len(check_result_info_list) == 0:
            return NO_DATA, res

        res['result'] = self._check_result_to_dict(check_result_info_list)

        return SUCCEED, res

    @staticmethod
    def _check_result_to_dict(check_result_info_list: List) -> Dict[str, Any]:
        """
            turn check result list to dict
        """
        result = {}
        for result_info in check_result_info_list:
            if result_info.host_id not in result:
                result[result_info.host_id] = {}
                result[result_info.host_id]['host_name'] = result_info.host_name
                result[result_info.host_id]['host_ip'] = result_info.host_ip
                result[result_info.host_id]['host_check_result'] = []
                result[result_info.host_id]['is_root'] = False
            if result_info.is_root is True:
                result[result_info.host_id]['is_root'] = True

            info = {
                "time": result_info.time,
                "metric_name": result_info.metric_name,
                "metric_label": result_info.metric_label,
                "is_root": result_info.is_root
            }
            result[result_info.host_id]['host_check_result'].append(info)
        return result

    def _query_check_host_info(self, data):
        """
            query check host info from database
        Args:
            data(dict): parameter, e.g.
                {
                    "alert_id": "xxxx",
                    "username": "xxxx
                }

        Returns:
            sqlalchemy.engine.row.Row list
        """
        host_id_query = self.session.query(AlertHost.host_id,
                                           AlertHost.host_ip,
                                           AlertHost.host_name,
                                           AlertHost.alert_id). \
            filter(AlertHost.alert_id == data.get('alert_id')).subquery()

        check_result_info_list = self.session.query(host_id_query.c.alert_id,
                                                    host_id_query.c.host_id,
                                                    host_id_query.c.host_ip,
                                                    host_id_query.c.host_name,
                                                    HostCheckResult.time,
                                                    HostCheckResult.is_root,
                                                    HostCheckResult.metric_name,
                                                    HostCheckResult.metric_label
                                                    ). \
            join(host_id_query, HostCheckResult.host_id == host_id_query.c.host_id).all()
        return check_result_info_list

    def query_result_list(self, data: Dict[str, str]) -> Tuple[int, dict]:
        """
            query check result host list sorted by alert id

        Args:
            data(dict): param e.g
                {
                    'page': 'int',
                    'per_page': 'int',
                    'domain': 'string',
                    'level': 'string',
                    'confirmed': boolean,
                    'sort': 'time',
                    'direction': 'asc or desc',
                    'username': 'string'
                }

        Returns:
            int: status code
            dict: e.g
                {
                    "total_count": int,
                    "total_page": int,
                    "result": [
                        {
                            "alert_id": "alert_id",
                            "alert_name": "alert_name",
                            "confirmed": True or False,
                            "domain": "domain_name",
                            "host_num": int,
                            "level": "level info",
                            "time": xxxxxxxx,
                            "workflow_id": "workflow_id",
                            "workflow_name": "workflow_name"
                        },
                        ...
                    ]
                }
        """
        page = data.get('page')
        per_page = data.get('per_page')
        column = data.get('sort')
        direction = data.get('direction')

        filters = {DomainCheckResult.username == data.get('username')}

        if data.get('domain'):
            filters.add(DomainCheckResult.domain == data.get('domain'))

        if data.get('level'):
            filters.add(DomainCheckResult.level == data.get('level'))

        if data.get('confirmed') and data.get('confirmed').lower() == "true":
            filters.add(DomainCheckResult.confirmed == 1)
        elif data.get('confirmed'):
            filters.add(DomainCheckResult.confirmed == 0)

        res = {
            'total_count': 0,
            'total_page': 0,
            'result': []
        }
        check_result_host_query = self._query_check_result_host_list(filters)
        total_count = len(check_result_host_query.all())
        check_result_host_list, total_page = sort_and_page(check_result_host_query, column,
                                                           direction, per_page, page)
        res['result'] = self._check_result_host_rows_to_list(check_result_host_list)
        res['total_page'] = total_page
        res['total_count'] = total_count

        return SUCCEED, res

    def _query_check_result_host_list(self, filters):
        """
            query needed check result list
        Args:
            filters (set): filter given by user

        Returns:
            sqlalchemy.orm.query.Query
        """
        host_count_query = self.session.query(AlertHost.alert_id,
                                              func.count(AlertHost.host_id).label('count')). \
            group_by(AlertHost.alert_id).subquery()

        check_result_host_query = self.session.query(DomainCheckResult.alert_id,
                                                     DomainCheckResult.alert_name,
                                                     DomainCheckResult.domain,
                                                     DomainCheckResult.time,
                                                     DomainCheckResult.workflow_id,
                                                     DomainCheckResult.workflow_name,
                                                     DomainCheckResult.level,
                                                     DomainCheckResult.confirmed,
                                                     host_count_query.c.count). \
            join(host_count_query,
                 DomainCheckResult.alert_id == host_count_query.c.alert_id).filter(*filters)
        return check_result_host_query

    @staticmethod
    def _check_result_host_rows_to_list(rows):
        """
            turn queried rows to list of dict
        Args:
            sqlalchemy.orm.query.Query
        Returns:
            list[dict]: e.g
                [
                    {
                        'alert_id': 'alert_id',
                        'alert_name': 'alert_name',
                        'domain': 'domain_name',
                        'time': int,
                        'workflow_id': 'workflow_id',
                        'level': 'level info',
                        'confirmed': 1 or 0,
                        'workflow_name': 'workflow_name',
                        'host_num': int
                    },
                    ...
                ]

        """
        res = []
        for row in rows:
            confirmed = True if row.confirmed == 1 else False
            check_result_host_info = {
                "alert_id": row.alert_id,
                "alert_name": row.alert_name,
                "domain": row.domain,
                "time": row.time,
                "workflow_id": row.workflow_id,
                "level": row.level,
                "confirmed": confirmed,
                "workflow_name": row.workflow_name,
                "host_num": row.count
            }
            res.append(check_result_host_info)
        return res
