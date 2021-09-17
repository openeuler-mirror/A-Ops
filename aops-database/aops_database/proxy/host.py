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
Description: Host table operation
"""
import math
import sqlalchemy
from sqlalchemy.sql.expression import desc, asc
from sqlalchemy import func

from aops_utils.log.log import LOGGER
from aops_database.function.helper import judge_return_code
from aops_database.proxy.proxy import MysqlProxy, ElasticsearchProxy
from aops_database.factory.table import Host, HostGroup, User
from aops_database.conf.constant import HOST_INFO_INDEX
from aops_utils.restful.status import DATABASE_DELETE_ERROR, DATABASE_INSERT_ERROR,\
    DATABASE_QUERY_ERROR, DATA_DEPENDENCY_ERROR, DATA_EXIST, SUCCEED


class HostDatabase(MysqlProxy):
    """
    Host related table operation
    """

    def add_host(self, data):
        """
        Add host to table

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "admin"
                    "host_list": [
                        {
                            "host_name": "host1",
                            "host_group_name": "group1",
                            "host_id": "id1",
                            "public_ip": "127.0.0.1",
                            "management": False,
                            "ssh_port": 22
                        }
                    ]
                }

        Returns:
            int
        """
        group_map = {}
        result = {
            "succeed_list": [],
            "fail_list": []
        }
        try:
            user = self.session.query(User).filter(
                User.username == data['username']).first()
            host_groups = user.host_groups
            hosts = user.hosts
            # create a map that map host_group_name to host_group
            group_map = dict(
                map(lambda item: (item.host_group_name, item), host_groups))
            for host_info in data['host_list']:
                host_group = group_map.get(host_info['host_group_name'])
                if host_group is None:
                    result['fail_list'].append(host_info)
                    continue
                host_group.host_count += 1
                host_info['host_group_id'] = host_group.host_group_id
                host_info['user'] = data['username']
                host = Host(**host_info)
                if host in hosts:
                    LOGGER.error("host %s exist", host_info['host_name'])
                    result['fail_list'].append(host_info)
                    continue
                host.host_group = host_group
                host.owner = user
                self.session.add(host)
                self.session.commit()
                result['succeed_list'].append(host_info)
            status_code = judge_return_code(result, DATABASE_INSERT_ERROR)
            return status_code, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("add host fail")
            self.session.rollback()
            result['fail_list'] = result['succeed_list'] + result['fail_list']
            result['succeed_list'] = []
            return DATABASE_INSERT_ERROR, result

    def delete_host(self, data):
        """
        Delete host from table

        Args:
            data(dict): parameter, e.g.
                {
                    "host_list": ["host1", "host2"],
                    "username": "admin"
                }

        Returns:
            int
        """
        host_list = data['host_list']
        result = {
            "succeed_list": [],
            "fail_list": []
        }
        host_info = {}
        try:
            # query matched host
            hosts = self.session.query(Host).filter(
                Host.host_id.in_(host_list)).all()
            for host in hosts:
                host_group = host.host_group
                host_group.host_count -= 1
                self.session.delete(host)
                result['succeed_list'].append(host.host_id)
                host_info[host.host_id] = host.host_name
            self.session.commit()
            result['fail_list'] = list(set(host_list) - set(result['succeed_list']))
            status_code = judge_return_code(result, DATABASE_DELETE_ERROR)
            result['host_info'] = host_info
            return status_code, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("delete host %s fail", host_list)
            self.session.rollback()
            result['fail_list'] = host_list
            result['succeed_list'] = []
            return DATABASE_DELETE_ERROR, result

    def get_host(self, data):
        """
        Get host according to host group from table

        Args:
            data(dict): parameter, e.g.
                {
                    "host_group_list": ["group1", "group2"]
                    "management": False
                }

        Returns:
            int: status code
            dict: query result
        """
        result = {}
        try:
            result = self._sort_host_by_column(data)
            self.session.commit()
            LOGGER.info("query host succeed")
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("query host fail")
            return DATABASE_QUERY_ERROR, result

    def get_host_count(self, data):
        """
        Get host count

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "admin
                }

        Returns:
            int: status code
            dict: query result
        """
        result = {}
        result['host_count'] = 0
        try:
            filters = self._get_host_filters(data)
            total_count = self._get_host_count(filters)
            result['host_count'] = total_count
            self.session.commit()
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("query host count fail")
            return DATABASE_QUERY_ERROR, result

    def _get_host_count(self, filters):
        """
        Query according to filters

        Args:
            filters(set): query filters

        Returns:
            int
        """
        total_count = self.session.query(func.count(
            Host.host_id)).filter(*filters).scalar()
        return total_count

    @staticmethod
    def _get_host_filters(data):
        """
        Generate filters

        Args:
            data(dict)

        Returns:
            set
        """
        username = data['username']
        host_group_list = data.get('host_group_list')
        management = data.get('management')
        filters = {
            Host.user == username
        }
        if host_group_list:
            filters.add(Host.host_group_name.in_(host_group_list))
        if management is not None:
            filters.add(Host.management == management)

        return filters

    def _sort_host_by_column(self, data):
        """
        Sort host info by specified column

        Args:
            data(dict): sorted condition info

        Returns:
            dict
        """
        result = {
            "total_count": 0,
            "total_page": 0,
            "host_infos": []
        }
        sort = data.get('sort')
        direction = desc if data.get('direction') == 'desc' else asc
        page = data.get('page')
        per_page = data.get('per_page')
        total_page = 1
        filters = self._get_host_filters(data)
        total_count = self._get_host_count(filters)
        if total_count == 0:
            return result

        if sort:
            if page and per_page:
                total_page = math.ceil(total_count / per_page)
                hosts = self.session.query(Host).filter(*filters).\
                    order_by(direction(getattr(Host, sort))).\
                    offset((page - 1) * per_page).\
                    limit(per_page).all()
            else:
                hosts = self.session.query(Host).filter(
                    *filters).order_by(direction(getattr(Host, sort))).all()
        else:
            if page and per_page:
                total_page = math.ceil(total_count / per_page)
                hosts = self.session.query(Host).filter(
                    *filters).offset((page - 1) * per_page).limit(per_page).all()
            else:
                hosts = self.session.query(Host).filter(
                    *filters).all()

        for host in hosts:
            host_info = {
                "host_id": host.host_id,
                "host_name": host.host_name,
                "host_group_name": host.host_group_name,
                "public_ip": host.public_ip,
                "ssh_port": host.ssh_port,
                "management": host.management,
                "status": host.status
            }
            result['host_infos'].append(host_info)

        result['total_page'] = total_page
        result['total_count'] = total_count

        return result

    def get_host_info(self, data):
        """
        Get host basic info according to host id from table

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "admin"
                    "host_list": ["id1", "id2"]
                }

        Returns:
            int: status code
            dict: query result
        """
        username = data['username']
        host_list = data.get('host_list')
        temp_res = []
        result = {}
        result['host_infos'] = temp_res
        query_fields = [Host.host_id, Host.host_name, Host.public_ip,
                        Host.ssh_port, Host.host_group_name, Host.management,
                        Host.status]
        filters = {
            Host.user == username
        }
        if host_list:
            filters.add(Host.host_id.in_(host_list))
        try:
            hosts = self.session.query(*query_fields).filter(*filters).all()
            for host in hosts:
                host_info = {
                    "host_id": host.host_id,
                    "host_group_name": host.host_group_name,
                    "host_name": host.host_name,
                    "public_ip": host.public_ip,
                    "ssh_port": host.ssh_port,
                    "management": host.management,
                    "status": host.status
                }
                temp_res.append(host_info)
            self.session.commit()
            LOGGER.info("query host %s basic info succeed", host_list)
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("query host %s basic info fail", host_list)
            return DATABASE_QUERY_ERROR, result

    def get_total_host_info_by_user(self, data):
        """
        Get host basic info according to user from table

        Args:
            data(dict): parameter, e.g.
                {
                    "username": ["admin"]
                }

        Returns:
            int: status code
            dict: query result
        """
        username = data.get('username')
        temp_res = {}
        result = {}
        result['host_infos'] = temp_res

        try:
            if username:
                users = self.session.query(User).filter(
                    User.username.in_(username)).all()
            else:
                users = self.session.query(User).all()
            for user in users:
                name = user.username
                temp_res[name] = []
                for host in user.hosts:
                    host_info = {
                        "host_id": host.host_id,
                        "host_group_name": host.host_group_name,
                        "host_name": host.host_name,
                        "public_ip": host.public_ip,
                        "ssh_port": host.ssh_port
                    }
                    temp_res[name].append(host_info)
            self.session.commit()
            LOGGER.info("query host basic info succeed")
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("query host basic info fail")
            return DATABASE_QUERY_ERROR, result

    def add_host_group(self, data):
        """
        Add host group to table

        Args:
            data(dict): parameter, e.g.
                {
                    "host_group_name": "group1",
                    "description": "des",
                    "username": "admin",
                }

        Returns:
            int
        """
        username = data['username']
        host_group_name = data['host_group_name']
        try:
            user = self.session.query(User).filter(
                User.username == username).first()
            host_group = HostGroup(**data)
            if host_group in user.host_groups:
                return DATA_EXIST
            host_group.user = user
            self.session.add(host_group)
            self.session.commit()
            LOGGER.info("add host group [%s] succeed", host_group_name)
            return SUCCEED
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            self.session.rollback()
            LOGGER.error("add host group [%s] fail", host_group_name)
            return DATABASE_INSERT_ERROR

    def delete_host_group(self, data):
        """
        Delete host group from table

        Args:
            data(dict): parameter, e.g.
                {
                    "host_group_list": ["group1"],
                    "username": "admin"
                }

        Returns:
            int: status code
            dict: deleted group
        """

        host_group_list = data['host_group_list']
        username = data['username']
        result = {"deleted": []}
        deleted = []
        not_deleted = []
        try:
            # Filter the group if there are hosts in the group
            host_groups = self.session.query(HostGroup).\
                filter(HostGroup.username == username).\
                filter(HostGroup.host_group_name.in_(host_group_list)).all()
            for host_group in host_groups:
                if host_group.host_count > 0:
                    not_deleted.append(host_group.host_group_name)
                    continue
                deleted.append(host_group.host_group_name)
                self.session.delete(host_group)
            self.session.commit()
            result["deleted"] = deleted
            if not_deleted:
                LOGGER.error(
                    "host group %s deleted, groups %s delete fail", deleted, not_deleted)
                return DATA_DEPENDENCY_ERROR, result
            LOGGER.info("host group %s delete succeed", deleted)
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            self.session.rollback()
            LOGGER.error("delete host group %s fail", host_group_list)
            return DATABASE_DELETE_ERROR, result

    def get_host_group(self, data):
        """
        Get host group from table

        Args:
            data(dict): parameter, e.g.
                {
                    "sort": "host_group_name",
                    "direction": "asc",
                    "page": 1,
                    "per_page": 20,
                    "username": "admin"
                }

        Returns:
            int: status code
            dict: group infos
        """
        result = {}
        try:
            result = self._sort_group_by_column(data)
            self.session.commit()
            LOGGER.info("query host group succeed")
            return SUCCEED, result
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.debug(error)
            LOGGER.error("query host group fail")
            return DATABASE_QUERY_ERROR, result

    def _sort_group_by_column(self, data):
        """
        Sort group info by specified column

        Args:
            data(dict): sorted condition info

        Returns:
            dict
        """
        result = {
            "total_count": 0,
            "total_page": 0,
            "host_group_infos": []
        }
        sort = data.get('sort')
        direction = desc if data.get('direction') == 'desc' else asc
        page = data.get('page')
        per_page = data.get('per_page')
        total_page = 1

        user = self.session.query(User).filter(
            User.username == data['username']).first()
        total_count = len(user.host_groups)
        if total_count == 0:
            return result
        query_fields = [HostGroup.host_group_name,
                        HostGroup.description, HostGroup.host_count]
        filters = {HostGroup.username == data['username']}
        if sort:
            if page and per_page:
                total_page = math.ceil(total_count / per_page)
                host_groups = self.session.query(*query_fields).filter(*filters).\
                    order_by(direction(getattr(HostGroup, sort))).\
                    offset((page - 1) * per_page).limit(per_page).all()
            else:
                host_groups = self.session.query(*query_fields).filter(*filters).\
                    order_by(direction(getattr(HostGroup, sort))).all()
        else:
            if page and per_page:
                total_page = math.ceil(total_count / per_page)
                host_groups = self.session.query(*query_fields).filter(*filters).\
                    offset((page - 1) * per_page).limit(per_page).all()
            else:
                host_groups = self.session.query(
                    *query_fields).filter(*filters).all()

        for host_group in host_groups:
            result['host_group_infos'].append({
                "host_group_name": host_group.host_group_name,
                "description": host_group.description,
                "host_count": host_group.host_count
            })

        result['total_page'] = total_page
        result['total_count'] = total_count

        return result


class HostInfoDatabase(ElasticsearchProxy):
    """
    Host info related operation
    """

    def save_host_info(self, data):
        """
        Save host info

        Args:
            data(dict): parameter, e.g.
                {
                    "host_infos: [...]
                }

        Returns:
            int
        """
        host_infos = data.get('host_infos')
        res = self.insert_bulk(HOST_INFO_INDEX, host_infos)
        if res:
            LOGGER.info("save host info succeed")
            return SUCCEED
        LOGGER.error("save host info fail")
        return DATABASE_INSERT_ERROR

    def delete_host_info(self, data):
        """
        Delete host info

        Args:
            data(dict): parameter, e.g.
                {
                    "host_list": ["id1"]
                }

        Returns:
            int
        """
        host_list = data.get('host_list')
        body = {
            "query": {
                "terms": {
                    "host_id": host_list
                }
            }
        }
        res = self.delete(HOST_INFO_INDEX, body)
        if res:
            LOGGER.info("delete host info of %s succeed", host_list)
            return SUCCEED
        LOGGER.error("delete host info of %s fail", host_list)
        return DATABASE_DELETE_ERROR

    def get_host_info(self, data):
        """
        Get host info

        Args:
            data(dict): parameter, e.g.
                {
                    "host_list": ["id1"]
                }

        Returns:
            int: status code
            dict
        """
        host_list = data.get('host_list')
        body = {
            "query": {
                "terms": {
                    "host_id": host_list
                }
            }
        }
        result = {}
        result['host_infos'] = []
        res = self.scan(HOST_INFO_INDEX, body)
        if res[0]:
            LOGGER.info("query host %s info succeed", host_list)
            result['host_infos'] = res[1]
            return SUCCEED, result
        LOGGER.error("query host %s info fail", host_list)
        return DATABASE_QUERY_ERROR, result
