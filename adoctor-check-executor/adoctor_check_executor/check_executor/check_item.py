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
Author: YangYunYi
Date: 2021/8/4 19:12
docs: check_item.py
description: Check item and check item manager
"""
from aops_utils.log.log import LOGGER
from adoctor_check_executor.common.check_error import CheckItemError, CheckExceptionList
from adoctor_check_executor.common.constant import MAIN_DATA_MACRO, CheckResultType
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.common.check_msg import CheckMsgToolKit
from adoctor_check_executor.check_executor.check_rule_manager import check_rule_manager
from adoctor_check_executor.check_executor.data_manager import DataManager


class CheckItemDetail:
    """
    Record check item details.

    Attributes:
        check_item_name (str): cache of check item
        data_list (list): data list
        check_condition (str): check condition
        check_result_description (str): check item description
        user (str): user of check item
    """

    def __init__(self, user, check_item_info):
        """
        Constructor

        Args:
            user (str): user of check item
            check_item_info (dict): info of check item
        """
        check_item_name = check_item_info.get("check_item")
        data_list = check_item_info.get("data_list", [])
        check_condition = check_item_info.get("condition")
        if not all([check_item_name, data_list, check_condition, user]):
            LOGGER.error("Invalid check item info.")
            raise CheckItemError("Invalid check item")
        self.check_item_name = check_item_name
        self.data_list = data_list
        self.check_condition = check_condition
        self.user = user
        self.check_rule_plugin_name = check_item_info.get("plugin") or "expression_rule_plugin"
        LOGGER.debug("check_rule_plugin_name %s", self.check_rule_plugin_name)
        self.check_result_description = check_item_info.get("description", "")

    def get_check_item_detail(self):
        """
        Add check item detail dict
        Args:

        Returns:
            data_info (dict)
        """
        data_info = dict()
        data_info["data_list"] = self.data_list
        data_info["check_item"] = self.check_item_name
        data_info["condition"] = self.check_condition
        data_info["plugin"] = self.check_rule_plugin_name
        data_info["description"] = self.check_result_description
        data_info["username"] = self.user
        return data_info


class CheckItem:
    """
    The manager of check item

    Attributes:
        host_list (list): host list
        data_manager (DataManager): data manager
        rule_plugin (CheckRulePlugin): check rule plugin
    """

    def __init__(self, check_item_detail):
        """
        Constructor
        Args:
            check_item_detail (CheckItemDetail): cache of check item

        Raise:
            CheckItemError
        """
        if not check_item_detail:
            LOGGER.error("check_item_detail is None")
            raise CheckItemError("check_item_detail is none")
        self.check_item_detail = check_item_detail
        self.host_list = []
        self.data_manager = None
        try:
            self.rule_plugin = check_rule_manager.get_plugin(
                check_item_detail.check_rule_plugin_name)
            self.rule_plugin.analysis_expression(check_item_detail.check_condition)
        except CheckExceptionList as exp:
            LOGGER.error("Check item load plugin failed.")
            raise CheckItemError from exp

    def _check_host_by_timestamp(self, start_index, host_data_vector, host_id, abnormal_data_list):
        """
        check host by time stamp
        Args:
            start_index (int): time range to do check
            host_list (list): host list to do check
        """
        sample_period = executor_check_config.executor.get("SAMPLE_PERIOD")
        for index in range(start_index, len(host_data_vector[MAIN_DATA_MACRO])):
            try:
                if not self.rule_plugin.judge_condition(index,
                                                        host_data_vector,
                                                        MAIN_DATA_MACRO):
                    continue
                # add exception data
                LOGGER.info("CheckItem %s do_check exception find",
                            self.check_item_detail.check_item_name)
                cur_timestamp = host_data_vector[MAIN_DATA_MACRO][index][0]
                abnormal_time_range = [cur_timestamp, cur_timestamp]
                self.add_abnormal_data(self.check_item_detail, abnormal_time_range,
                                       host_id, CheckResultType.abnormal,
                                       abnormal_data_list)
            except CheckExceptionList as exp:
                LOGGER.error("judge_condition exp %s" % exp)
                cur_timestamp = host_data_vector[MAIN_DATA_MACRO][index][0]
                abnormal_time_range = [cur_timestamp, cur_timestamp]
                self.add_abnormal_data(self.check_item_detail, abnormal_time_range,
                                       host_id, CheckResultType.internal_error,
                                       abnormal_data_list)

    def do_check(self, time_range, host_list):
        """
        do check
        Args:
            time_range (list): time range to do check
            host_list (list): host list to do check
        """
        LOGGER.debug("--------------------start do check %s, "
                     "time_range %s, host_list %s--------------------",
                     self.check_item_detail.check_item_name, time_range, host_list)
        abnormal_data_list = []
        self.prepare_data(time_range, host_list, abnormal_data_list)

        for host in self.host_list:
            host_ip = host.get("public_ip")
            host_id = host.get("host_id")
            host_data_vector = self.data_manager.host_cache.get(host_ip)
            if not host_data_vector or \
                    sorted(self.data_manager.data_name_map.values()) != \
                    sorted(host_data_vector.keys()):
                LOGGER.debug("No data of host %s:%s", host_ip, host_id)
                self.add_abnormal_data(self.check_item_detail, time_range, host_id,
                                       CheckResultType.nodata, abnormal_data_list)
                continue

            start_index = self.data_manager.find_start_index(host_ip,
                                                             MAIN_DATA_MACRO,
                                                             time_range[0])
            if start_index == -1:
                LOGGER.warning("No data of host %s:%s", host_ip, host_id)
                self.add_abnormal_data(self.check_item_detail, time_range, host_id,
                                       CheckResultType.nodata, abnormal_data_list)
                continue

            self._check_host_by_timestamp(start_index, host_data_vector,
                                          host_id, abnormal_data_list)
        return abnormal_data_list

    @staticmethod
    def add_abnormal_data(check_item_detail, time_range, host_id, result_value, abnormal_data_list):
        """
        Add abnormal data to list
        Args:
            check_item_detail (CheckItemDetail): check item detail of check item
            time_range (list): time
            host_id (str): host id
            result_value (str): check result
            abnormal_data_list (list): the list to record abnormal data
        """
        abnormal_data = CheckMsgToolKit.build_abnormal_data(check_item_detail, time_range,
                                                            host_id, result_value)
        abnormal_data_list.append(abnormal_data)

    def prepare_data(self, time_range, host_list, abnormal_data_list):
        """
        prepare data before check
        Args:
            time_range (list): time range to prepare data
            host_list (list): host list to do prepare data
            abnormal_data_list (list): Record the abnormal data
        """
        self.host_list = host_list
        self.data_manager = DataManager(self.check_item_detail.data_list,
                                        self.host_list)
        new_time_range = [time_range[0] - self.rule_plugin.time_shift, time_range[1]]

        LOGGER.debug("new time start %s, time_shift %s", new_time_range,
                     self.rule_plugin.time_shift)
        self.data_manager.query_data(self.host_list, self.check_item_detail,
                                     new_time_range, abnormal_data_list)
