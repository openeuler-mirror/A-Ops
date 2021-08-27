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
from aops_database.proxy.deploy import DeployDatabase
from aops_database.views import BaseResource


class AddTask(BaseResource):
    """
    Interface for add Task
    Restful API: POST
    """

    def post(self):
        """
        Add task

        Args:
            task_name(str)
            description(str)
            task_id(str)
            template_name(list)
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('add_task', DeployDatabase())


class DeleteTask(BaseResource):
    """
    Interface for delete Task
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete task

        Args:
            task_list(list): task id list
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('delete_task', DeployDatabase())


class GetTask(BaseResource):
    """
    Interface for get Task
    Restful API: POST
    """

    def post(self):
        """
        Get task

        Args:
            task_list(list): task id list
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        return self.do_action('get_task', DeployDatabase())


class AddTemplate(BaseResource):
    """
    Interface for add template
    Restful API: POST
    """

    def post(self):
        """
        Add template

        Args:
            template_name(str): template name
            template_content(dict): content
            description(str)
            username(str)

        Returns:
            dict: response body
        """
        return self.do_action('add_template', DeployDatabase())


class GetTemplate(BaseResource):
    """
    Interface for get template info.
    Restful API: POST
    """

    def post(self):
        """
        Get template info

        Args:
            template_list(list): template id list
            username(str)
            sort(str): sort according to specified field
            direction(str): sort direction
            page(int): current page
            per_page(int): count per page

        Returns:
            dict: response body
        """
        return self.do_action('get_template', DeployDatabase())


class DeleteTemplate(BaseResource):
    """
    Interface for delete template.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete template

        Args:
            template_list(list): template name list

        Returns:
            dict: response body
        """
        return self.do_action('delete_template', DeployDatabase())
