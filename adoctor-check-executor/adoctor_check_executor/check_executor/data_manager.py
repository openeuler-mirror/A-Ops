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
Date: 2021/8/7 21:36
docs: check_task.py
description: Check task
"""
import json
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import SUCCEED
from aops_utils.preprocessing.alignment import align
from adoctor_check_executor.common.constant import CheckResultType
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.common.check_msg import CheckMsgToolKit


class DataManager:
    """
    The manager of data

    Attributes:
        host_cache (list): check item list
    """

    def __init__(self, data_list, host_list):
        self.host_cache = dict()
        self.data_list = data_list
        self.data_name_map = {}
        self.data_type = "kpi"
        self._parse_data_list()
        self._init_cache(host_list)

    def _parse_data_list(self):
        """
        Parse data list. Add macro and data_name_str attribute
        """
        # $index mean the num index data item in list
        index = 0
        has_log = False
        for data_info in self.data_list:
            data_info["macro"] = "${}".format(index)
            data_name = data_info.get("name")
            label_dict = data_info.get("label", {})
            label_config = json.dumps(sorted(label_dict.items(), key=lambda x: x[1]))
            data_info["data_name_str"] = data_name + label_config
            self.data_name_map[data_info["data_name_str"]] = data_info["macro"]
            if data_info.get("type") == "log":
                has_log = True
            index += 1
        self.data_type = "log" if has_log else "kpi"

    def _init_cache(self, host_list):
        """
        Init the data list cache by host list
            self.host_cache = {
                "host_ip1": {},
                "host_ip2": {},
            }
        Args:
            host_list (list): host list to be cached
                              [ {"host_id":"XXXXX", "public_ip": "x.x.x.x"},
                              {"host_id":"YYYYY", "public_ip": "y.y.y.y"}]

        Returns:
            None

        """
        for host in host_list:
            host_ip = host.get("public_ip")
            if not host_ip:
                LOGGER.error("Without host ip %s", host_ip)
                continue
            self.host_cache[host_ip] = dict()

    def find_start_index(self, host_ip, data_macro_name, start_time_stamp):
        """
        Get the first data index which time stamp >= the start time stamp
        Args:
            host_ip (str): host ip to find the data list
            data_macro_name (str): the data macro name in data list
            start_time_stamp (int): the target start time stamp

        Return:
            index (int)

        """
        if not all([host_ip, data_macro_name]):
            LOGGER.error("host info is invalid, public ip is none")
            return -1
        if host_ip not in self.host_cache.keys() or \
                data_macro_name not in self.host_cache.get(host_ip).keys():
            LOGGER.error("host_ip %s or data_macro_name %s is not in host_cache",
                         host_ip, data_macro_name)
            return -1

        left = 0
        right = len(self.host_cache[host_ip][data_macro_name]) - 1
        if self.host_cache[host_ip][data_macro_name][left][0] >= start_time_stamp:
            return left
        if self.host_cache[host_ip][data_macro_name][right][0] < start_time_stamp:
            return -1

        while left <= right:
            mid = left + (right - left) // 2

            if self.host_cache[host_ip][data_macro_name][mid][0] == start_time_stamp:
                LOGGER.debug("host_ip %s, data_macro_name %s start_time_stamp %s, index %s",
                             host_ip, data_macro_name, start_time_stamp, mid)
                return mid
            if self.host_cache[host_ip][data_macro_name][mid][0] <= start_time_stamp:
                left = mid + 1
            elif self.host_cache[host_ip][data_macro_name][mid][0] > start_time_stamp:
                right = mid - 1

        ret = -1 if left == len(self.host_cache[host_ip][data_macro_name]) else left
        LOGGER.debug("host_ip %s, data_macro_name %s start_time_stamp %s, index %s",
                     host_ip, data_macro_name, start_time_stamp, ret)
        return ret

    def query_data(self, host_list, check_item_detail, time_range, abnormal_data_list):
        """
        Get the first data index which time stamp >= the start time stamp
        Args:
            host_list (list): host list to query data
            check_item_detail (CheckItemDetail): check item detail record the check item basic info
            time_range (list): time range to query data
            abnormal_data_list (list): Records the list of exceptions that fail to request data.
        """
        for host in host_list:
            host_ip = host.get("public_ip")
            response = CheckMsgToolKit.get_data_from_database(time_range,
                                                              host_ip,
                                                              check_item_detail.data_list)
            if response.get("code") != SUCCEED or response.get("fail_list"):
                LOGGER.error("Get data failed %s", response)
                abnormal_data = CheckMsgToolKit.build_abnormal_data(check_item_detail,
                                                                    time_range,
                                                                    host.get("host_id"),
                                                                    CheckResultType.internal_error)
                abnormal_data_list.append(abnormal_data)
                LOGGER.error("Get data from data base failed. time_range %s, host:%s",
                             time_range, host.get("host_id"))
                continue

            data_infos = response.get("succeed_list")
            if not data_infos:
                # No data exception is recorded here.
                # If no data is found during the check, perform the data exception.
                LOGGER.error("Get no data from data base. time_range %s, host:%s",
                             time_range, host.get("host_id"))
                continue

            for data_info in data_infos:
                data_name = data_info.get("name")
                label_dict = data_info.get("label", {})
                label_config_str = json.dumps(sorted(label_dict.items(), key=lambda x: x[1]))
                data_name_str = data_name + label_config_str
                # key is $i
                self.host_cache[host_ip][self.data_name_map.get(data_name_str)] \
                    = data_info.get("values")

            if self.data_type != "log":
                LOGGER.debug("Align kpi data for host %s", host)
                self.host_cache[host_ip] = \
                    align(executor_check_config.executor.get("SAMPLE_PERIOD"),
                          time_range,
                          self.host_cache.get(host_ip))
