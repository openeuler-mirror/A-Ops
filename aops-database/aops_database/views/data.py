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
from collections import defaultdict
from flask import request
from flask import jsonify
from flask_restful import Resource

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import make_response, DATABASE_QUERY_ERROR, SUCCEED
from aops_database.function.helper import operate, combine_return_codes
from aops_database.proxy.data import LogDatabase, KpiDataBase


def split_get_request_args(args):
    """
    Split get data request's args into 2 part, Es and prometheus
    Args:
        args: args of get data request, format is list in "get" function.

    Returns:
        dict
    """
    time_range = args["time_range"]
    hosts_info = args["data_infos"]

    es_hosts = []
    prom_hosts = []

    all_match = SUCCEED

    for host_info in hosts_info:
        data_list = host_info["data_list"]
        data_in_es = []
        data_in_prom = []

        for data in data_list:
            data_type = data["type"]
            if data_type == "log":
                # the data in elasticsearch doesn't have label
                data_in_es.append(data["name"])
            elif data_type == "kpi":
                data_in_prom.append(data)
            else:
                LOGGER.error("Data item %s of host %s type is unknown: '%s'"
                             % (data["name"], host_info["host_id"], data_type))

                all_match = DATABASE_QUERY_ERROR

        if data_in_prom:
            prom_host = {"host_id": host_info["host_id"], "data_list": data_in_prom}
            prom_hosts.append(prom_host)

        if data_in_es:
            es_host = {"host_id": host_info["host_id"], "data_list": data_in_es}
            es_hosts.append(es_host)

    splited_args = {"es": {"time_range": time_range, "data_infos": es_hosts},
                    "prom": {"time_range": time_range, "data_infos": prom_hosts},
                    "all_match": all_match}

    return splited_args


class GetData(Resource):
    """
    Interface for get data.
    Restful API: post
    """
    @staticmethod
    def post():
        """
        Get raw data (log and kpi) from elasticsearch and prometheus

        Args:
            e.g.
            {
                "time_range": [1111,2222],
                "data_infos": [
                    {
                        "host_id": "host1",
                        "data_list": [
                            {
                                "name": "node_cpu",
                                "type": "kpi",
                                "label": {
                                    "cpu": "cpu1",
                                    "mode": "idle"
                                }
                            },
                            {
                                "name": "history",
                                "type": "log"
                            }
                        ]
                    }
                ]
            }
        Returns:

        """
        args = request.get_json()
        LOGGER.debug(args)

        splited_args = split_get_request_args(args)

        es_args = splited_args["es"]
        prom_args = splited_args["prom"]
        all_match = splited_args["all_match"]

        action = 'get_data'
        log_status_code = kpi_status_code = SUCCEED
        data = defaultdict(list)

        if es_args["data_infos"]:
            log_proxy = LogDatabase()
            log_status_code, log_data = operate(log_proxy, es_args, action)
            data["succeed_list"].extend(log_data["succeed_list"])
            data["fail_list"].extend(log_data["fail_list"])
        if prom_args["data_infos"]:
            kpi_proxy = KpiDataBase()
            kpi_status_code, kpi_data = operate(kpi_proxy, prom_args, action)
            data["succeed_list"].extend(kpi_data["succeed_list"])
            data["fail_list"].extend(kpi_data["fail_list"])

        # get final status based on query results, and if all data's type are recognized
        status_code = combine_return_codes(DATABASE_QUERY_ERROR, log_status_code,
                                           kpi_status_code, all_match)

        response = make_response((status_code, data))

        return jsonify(response)
