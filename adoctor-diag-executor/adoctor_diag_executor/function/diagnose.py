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
Description: Diagnose related functions
"""
import json
import uuid

from aops_utils.log.log import LOGGER
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import SUCCEED, PARTIAL_SUCCEED
from aops_utils.conf.constant import DATA_GET_CHECK_RESULT, DATA_SAVE_DIAG_REPORT
from aops_utils.restful.helper import make_datacenter_url
from adoctor_diag_executor.function.diag_tree import DiagTree
from adoctor_diag_executor.function.diag_exception import ExpressionError


def diagnose(message_value):
    """
    do diagnose based on message's value
    Args:
        message_value (dict): info of diagnose. e.g.:
            {
                "username": "admin",
                "host_id": "host1",
                "tree_name": "tree2",
                "tree_content": {}
                "time_range": [112221122, 112221222],
                "task_id": "5eaaea18061411ec8761a01c8d75c92f"
            }
    Returns:
        dict: report to save
    """
    user_name = message_value["username"]
    tree_dict = message_value.pop("tree_content")
    time_range = message_value.pop("time_range")
    message_value["start"] = time_range[0]
    message_value["end"] = time_range[1]
    message_value['report'] = ""
    message_value["report_id"] = _create_task_id()

    try:
        tree = DiagTree(tree_dict)
        tree_leaves = list(tree.check_items)
    # Normally trees get from database are all validate. In case of some strange
    # situations, add debug log.
    except KeyError as error:
        LOGGER.debug("Diagnose tree %s init failed, please check your tree's content. %s"
                     % (message_value["tree_name"], error))
        return message_value

    check_body = {
        "username": user_name,
        "time_range": time_range,
        "check_items": tree_leaves,
        "host_list": [message_value["host_id"]]
    }
    check_result = get_check_result(check_body)

    try:
        diag_res = tree.diagnose(check_result)
    # Normally trees get from database are all validate. In case of some strange
    # situations, add debug log.
    except ExpressionError as error:
        LOGGER.error("Diagnose tree init failed due to bad format. %s" % error)
        return message_value

    message_value['report'] = json.dumps(diag_res, ensure_ascii=False)
    return message_value


def get_check_result(pyload):
    """
    get check result from database and parse it into specific format
    Args:
        pyload (dict): request body
            {
                "username": user_name,
                "time_range": message_value["host"],
                "check_items": tree_leaves,
                "host_list": message_value["host"]
            }

    Returns:
        dict: parsed check result
    """
    check_result_url = make_datacenter_url(DATA_GET_CHECK_RESULT)
    response = MyResponse.get_response("POST", check_result_url, pyload)

    check_items = set(pyload["check_items"])
    parsed_result = parse_check_result(check_items, response)
    return parsed_result


def parse_check_result(check_items, response):
    """
    parse check result into four parts, no data, abnormal, normal and internal error
    Args:
        check_items (set): check items names set
        response (dict): list of check result dict
        e.g.:
        {
            "code": "",
            "msg": "",
            "total_count": 1,
            "total_page": 1,
            "check_result": [
                {"host_id": "host1", "data_list": ["data1", "data2"], "start": 11, "end": "25",
                "check_item": "check_item1", "condition": "", "value": "Abnormal"},
                {"host_id": "host1", "data_list": ["data2", "data3"], "start": 11, "end": "25",
                "check_item": "check_item2", "condition": "", "value": "No data"}
            ]
        }

    Returns:
        dict
    """

    parsed_result = {
        "abnormal": set(),
        "no data": set(),
        "internal error": set()
    }

    if response["code"] not in (SUCCEED, PARTIAL_SUCCEED):
        LOGGER.error("Request to get check result from database failed. %s" % response["msg"])
        parsed_result["internal error"] = check_items
        return parsed_result

    LOGGER.info("Request check result succeed.")
    result_list = response["check_result"]

    # if check item is not in database, then it will not appear in result list
    for item_result in result_list:
        if item_result["value"] == "Abnormal":
            parsed_result["abnormal"].add(item_result["check_item"])
        elif item_result["value"] == "No data":
            parsed_result["no data"].add(item_result["check_item"])
        elif item_result["value"] == "Internal error":
            parsed_result["internal error"].add(item_result["check_item"])
        else:
            parsed_result["internal error"].add(item_result["check_item"])
            LOGGER.error("Unknown flag %s of check item %s." % (item_result["value"],
                                                                item_result["check_item"]))

    return parsed_result


def save_diag_result(reports):
    """
    save diagnose result into data center

    Args:
        reports (dict): list of diagnose reports. e.g.:
            {
                "reports": [{
                    "username": "admin",
                    "host_id": "host1",
                    "tree_name": "tree2",
                    "tree_content": {}
                    "time_range": [112221122, 112221222],
                    "task_id": "5eaaea18061411ec8761a01c8d75c92f"}]
            }
        diag_res (dict): diagnose tree's dict

    Returns:

    """
    database_url = make_datacenter_url(DATA_SAVE_DIAG_REPORT)
    response = MyResponse.get_response("post", database_url, reports)

    if response["code"] != SUCCEED:
        LOGGER.error("Save %d diagnose reports failed with error: %s"
                     % (len(reports), response["msg"]))
    else:
        LOGGER.info("Save %d diagnose reports succeed." % len(reports["reports"]))


def _create_task_id():
    """
    create uuid without "-" because of elasticsearch restriction
    Returns:
        str
    """
    raw_uuid = str(uuid.uuid1())
    reformat_uuid = raw_uuid.replace("-", "")
    return reformat_uuid
