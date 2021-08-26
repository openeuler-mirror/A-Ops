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
Description: some helper function
"""
from aops_utils.conf import configuration
from aops_utils.conf.constant import URL_FORMAT


def make_datacenter_url(route):
    """
    make database center url

    Args:
        route(str)

    Returns:
        str: url
    """
    # make database center url
    database_ip = configuration.database.get("IP")  # pylint: disable=E1101
    database_port = configuration.database.get("PORT")  # pylint: disable=E1101
    database_url = URL_FORMAT % (database_ip, database_port, route)
    return database_url


def make_manager_url(route):
    """
    make manager center url

    Args:
        route(str)

    Returns:
        tuple: url, header
    """
    manager_ip = configuration.manager.get("IP")  # pylint: disable=E1101
    manager_port = configuration.manager.get("PORT")  # pylint: disable=E1101
    manager_url = URL_FORMAT % (manager_ip, manager_port, route)
    manager_header = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    return manager_url, manager_header


def make_diag_url(route):
    """
    make diag url

    Args:
        route(str)

    Returns:
        tuple: url, header
    """
    diag_ip = configuration.diagnose.get("IP")  # pylint: disable=E1101
    diag_port = configuration.diagnose.get("PORT")  # pylint: disable=E1101
    diag_url = URL_FORMAT % (diag_ip, diag_port, route)
    diag_header = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    return diag_url, diag_header
