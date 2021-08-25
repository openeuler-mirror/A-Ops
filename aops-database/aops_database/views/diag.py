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
Description: Restful apis about diag
"""
from aops_database.views import BaseResource
from aops_database.proxy.diag import DiagDatabase


class AddDiagTree(BaseResource):
    """
    Interface for add fault diagnose tree.
    Restful API: post
    """

    def post(self):
        """
        Add diag tree

        Args:
            username(str)
            trees(list)

        Returns:
            dict: response body
        """
        return self.do_action('import_diag_tree', DiagDatabase())


class DeleteDiagTree(BaseResource):
    """
    Interface for delete fault diagnose tree.
    Restful API: DELETE
    """

    def delete(self):
        """
        Delete diag tree

        Args:
            username(str)
            tree_list(list): tree name list

        Returns:
            dict: response body
        """
        return self.do_action('delete_diag_tree', DiagDatabase())


class GetDiagTree(BaseResource):
    """
    Interface for get fault diagnose tree.
    Restful API: POST
    """

    def post(self):
        """
        Get diag tree

        Args:
            username(str)
            tree_list(list): tree name list

        Returns:
            dict: response body
        """
        return self.do_action('get_diag_tree', DiagDatabase())


class SaveDiagReport(BaseResource):
    """
    Interface for save diag report.
    Restful API: post
    """

    def post(self):
        """
        Add diag report

        Args:
            reports(list): report list

        Returns:
            dict: response body
        """
        return self.do_action('save_diag_report', DiagDatabase())


class DeleteDiagReport(BaseResource):
    """
    Interface for delete diag report.
    Restful API: delete
    """

    def delete(self):
        """
        Delete host

        Args:
            username(str)
            report_list(list): report id list

        Returns:
            dict: response body
        """
        return self.do_action('delete_diag_report', DiagDatabase())


class GetDiagReportList(BaseResource):
    """
    Interface for get diag report list.
    Restful API: POST
    """

    def post(self):
        """
        Get diag report

        Args:
            username(str)
            time_range(list): time range
            host_list(list): host id list
            task_id(str): task id
            report_id(str): report id
            tree_list(list): tree name list
            sort(str)
            direction(str)
            page(int)
            per_page(int)

        Returns:
            dict: response body
        """
        return self.do_action('get_diag_report_list', DiagDatabase())


class GetDiagProcess(BaseResource):
    """
    Interface for get diag process.
    Restful API: POST
    """

    def post(self):
        """
        Get diag report

        Args:
            username(str)
            task_list(list): task id list

        Returns:
            dict: response body
        """
        return self.do_action('get_diag_process', DiagDatabase())


class GetDiagReport(BaseResource):
    """
    Interface for get diag report.
    Restful API: POST
    """

    def post(self):
        """
        Get diag report

        Args:
            username(str)
            report_list(list): report id list

        Returns:
            dict: response body
        """
        return self.do_action('get_diag_report', DiagDatabase())
