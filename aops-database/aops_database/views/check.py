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
Description: Restful apis about check
"""
from aops_database.views import BaseResource
from aops_database.proxy.check import CheckDatabase


class AddCheckRule(BaseResource):
    """
    Interface for add check rule.
    Restful API: post
    """

    def post(self):
        """
        Add check rule

        Args:
            username(str)
            check_items(list): check items info

        Returns:
            dict: response body
        """
        return self.do_action('add_check_rule', CheckDatabase())


class DeleteCheckRule(BaseResource):
    """
    Interface for delete check rule.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete check rule

        Args:
            username(str)
            check_items(list): check item name list

        Returns:
            dict: response body
        """
        return self.do_action('delete_check_rule', CheckDatabase())


class GetCheckRule(BaseResource):
    """
    Interface for get check rule.
    Restful API: POST
    """

    def post(self):
        """
        Get check rule

        Args:
            username(str)
            check_items(list): check item name list
            sort(str)
            direction(str)
            page(int)
            per_page(int)

        Returns:
            dict: response body
        """
        return self.do_action('get_check_rule', CheckDatabase())


class GetCheckRuleCount(BaseResource):
    """
    Interface for get check rule count.
    Restful API: POST
    """

    def post(self):
        """
        Get check rule count

        Args:
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('get_rule_count', CheckDatabase())


class SaveCheckResult(BaseResource):
    """
    Interface for save check result.
    Restful API: post
    """

    def post(self):
        """
        Save check result

        Args:
            check_results(list)

        Returns:
            dict: response body
        """
        return self.do_action('save_check_result', CheckDatabase())


class DeleteCheckResult(BaseResource):
    """
    Interface for delete check result.
    Restful API: delete
    """

    def delete(self):
        """
        Delete check result

        Args:
            username(str)
            host_list(list): host id list
            time_range(list): time range

        Returns:
            dict: response body
        """
        return self.do_action('delete_check_result', CheckDatabase())


class GetCheckResult(BaseResource):
    """
    Interface for get check result.
    Restful API: POST
    """

    def post(self):
        """
        Get check result

        Args:
            username(str)
            time_range(list): time range
            host_list(list): host id list
            check_items(list): check items list
            sort(str)
            direction(str)
            page(int)
            per_page(int)

        Returns:
            dict: response body
        """
        return self.do_action('get_check_result', CheckDatabase())


class GetCheckResultCount(BaseResource):
    """
    Interface for get check result count.
    Restful API: POST
    """

    def post(self):
        """
        Get check result count

        Args:
            username(str)
            host_list(list): host id list
            sort(str)
            direction(str)
            page(int)
            per_page(int)

        Returns:
            dict: response body
        """
        return self.do_action('get_check_result_count', CheckDatabase())
