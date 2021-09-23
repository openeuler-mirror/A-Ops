#!/usr/bin/python3
# -*- coding:UTF=8 -*-
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
Author: YangYunYi
Date: 2021/8/29 17:41
docs: msg_factory.py
description: check executor msg related
"""

from aops_utils.restful.helper import make_datacenter_url
from aops_utils.conf.constant import DATA_SAVE_CHECK_RESULT, DATA_GET_DATA, \
    DATA_GET_CHECK_RULE, DATA_GET_HOST_INFO_BY_USER, DATA_DELETE_CHECK_RESULT
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import SUCCEED
from aops_utils.log.log import LOGGER


class CheckMsgToolKit:
    """
    Check msg tool kit
    """

    @staticmethod
    def build_abnormal_data(check_item_detail, time_range, host_id, check_result):
        """
        build abnormal data
        Args:
            check_item_detail (CheckItemDetail): check item info detail
            time_range (list): time range to prepare data
            host_id (str): host id of check item
            check_result (str): check result
        """
        abnormal_data_info = check_item_detail.get_check_item_detail()
        abnormal_data_info["host_id"] = host_id
        abnormal_data_info["start"] = time_range[0]
        abnormal_data_info["end"] = time_range[1]
        abnormal_data_info["value"] = check_result
        LOGGER.debug("the abnormal_data_info %s", abnormal_data_info)
        return abnormal_data_info

    @staticmethod
    def save_check_result_to_database(abnormal_data_result):
        """
        Save Check result to data base
        Args:
            abnormal_data_result (list): abnormal data result
        """
        msg = {
            "check_results": abnormal_data_result
        }
        database_url = make_datacenter_url(DATA_SAVE_CHECK_RESULT)
        response = MyResponse.get_result(
            SUCCEED, 'post', database_url, msg)

        return response

    @staticmethod
    def delete_check_result_from_database(host_list, time_range, user_name, check_items):
        """
        Delete Check result from data base
        Args:
            host_list (list): the host list to be delete
            time_range (list): time range [start_ts, end_ts]
            user_name (str): the user of check result to be delete
            check_items(list): check item list
        """
        msg = {
            "host_list": host_list,
            "time_range": time_range,
            "username": user_name,
            "check_items": check_items
        }
        database_url = make_datacenter_url(DATA_DELETE_CHECK_RESULT)
        response = MyResponse.get_result(
            SUCCEED, 'delete', database_url, msg)
        if response.get("code") != SUCCEED:
            LOGGER.error("Delete check result host_list %s, "
                         "time_range %s, user_name %s failed",
                         host_list, time_range, user_name)
        return response


    @staticmethod
    def get_data_from_database(time_range, host_ip, data_list):
        """
        Get data from data base
        Args:
            time_range (list): time range
            host_ip (str): host ip
            data_list (list): data list
        """
        msg = {
            "time_range": time_range,
            "data_infos": [{"host_id": host_ip, "data_list": data_list}],
        }

        database_url = make_datacenter_url(DATA_GET_DATA)
        response = MyResponse.get_result(
            SUCCEED, 'post', database_url, msg)
        return response

    @staticmethod
    def get_check_rule_from_database(user):
        """
        Get check rule from data base
        Args:
            user (str): user of the check rule to query
        """
        msg = {
            "username": user,
            "check_items": []
        }

        database_url = make_datacenter_url(DATA_GET_CHECK_RULE)
        response = MyResponse.get_result(
            SUCCEED, 'post', database_url, msg)
        if response.get("code") != SUCCEED:
            return {}
        return response.get("check_items")

    @staticmethod
    def get_user_list_from_database():
        """
        Get user list from database
        """
        msg = {
            "username": []
        }
        database_url = make_datacenter_url(DATA_GET_HOST_INFO_BY_USER)
        response = MyResponse.get_result(
            SUCCEED, 'post', database_url, msg)
        if response.get("code") != SUCCEED:
            LOGGER.error("Get host_list failed")
            return []
        host_infos = response.get("host_infos")
        if not host_infos:
            LOGGER.error("No host_infos found in response")
            return []
        return list(host_infos.keys())
