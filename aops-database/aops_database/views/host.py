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
Description: Restful apis about host
"""
from flask import request, jsonify
from flask_restful import Resource

from aops_database.function.helper import SESSION, operate
from aops_database.proxy.host import HostDatabase, HostInfoDatabase
from aops_utils.restful.status import make_response
from aops_database.views import BaseResource


class AddHost(BaseResource):
    """
    Interface for add host.
    Restful API: post
    """

    def post(self):
        """
        Add host

        Args:
            host_id(str): unique id of host
            host_name(str): hostname
            host_group_name(str): group name
            public_ip(str): ip
            ssh_port(int): ssh port
            management(bool): whether it's a managment node
            user_name(str)

        Returns:
            dict: response body
        """
        return self.do_action('add_host', HostDatabase(), SESSION)


class DeleteHost(BaseResource):
    """
    Interface for delete host.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete host

        Args:
            host_list(list): host id list
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('delete_host', HostDatabase(), SESSION)


class GetHost(BaseResource):
    """
    Interface for get host.
    Restful API: POST
    """

    def post(self):
        """
        Get host

        Args:
            host_group_list(list): host group name list
            management(bool): whether it's a manage node
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        return self.do_action('get_host', HostDatabase(), SESSION)


class GetHostCount(BaseResource):
    """
    Interface for get host count
    Restful API: POST
    """

    def post(self):
        """
        Get host

        Args:
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('get_host_count', HostDatabase(), SESSION)


class AddHostGroup(BaseResource):
    """
    Interface for add host group.
    Restful API: post
    """

    def post(self):
        """
        Add host group

        Args:
            host_group_name(str): name
            description(str)
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('add_host_group', HostDatabase(), SESSION)


class DeleteHostGroup(BaseResource):
    """
    Interface for delete host group.
    Restful API: delete
    """

    def delete(self):
        """
        Delete host group

        Args:
            host_group_list(list): group name list
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('delete_host_group', HostDatabase(), SESSION)


class GetHostGroup(BaseResource):
    """
    Interface for get host group.
    Restful API: POST
    """

    def post(self):
        """
        Get host

        Args:
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('get_host_group', HostDatabase(), SESSION)


class GetHostInfo(Resource):
    """
    Interface for get host info.
    Restful API: POST
    """
    @staticmethod
    def post():
        """
        Get host info

        Args:
            host_list(list): host list
            basic(bool)
            username(str)

        Returns:
            dict: response body
        """
        args = request.get_json()
        basic = args.get('basic')
        if not basic:
            proxy = HostInfoDatabase()
            action = 'get_host_info'
            response = make_response(operate(proxy, args, action))
        else:
            proxy = HostDatabase()
            action = 'get_host_info'
            response = make_response(operate(proxy, args, action, SESSION))

        return jsonify(response)


class GetHostInfoByUser(BaseResource):
    """
    Interface for get host info by user.
    Restful API: POST
    """

    def post(self):
        """
        Get host info by user

        Args:
            username(list)

        Returns:
            dict: response body
        """
        return self.do_action('get_total_host_info_by_user', HostDatabase(), SESSION)


class SaveHostInfo(BaseResource):
    """
    Interface for save host info.
    Restful API: POST
    """

    def post(self):
        """
        Save host info

        Args:
            host_infos(list): host info list

        Returns:
            dict: response body
        """
        return self.do_action('save_host_info', HostInfoDatabase())


class DeleteHostInfo(BaseResource):
    """
    Interface for delete host info.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete host info

        Args:
            host_list(list): host id list

        Returns:
            dict: response body
        """
        return self.do_action('delete_host_info', HostInfoDatabase())
