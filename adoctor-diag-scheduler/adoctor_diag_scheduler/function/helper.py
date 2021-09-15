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
help functions for producer
"""
import time

from aops_utils.restful.status import SUCCEED
from aops_utils.conf.constant import DATA_GET_DIAG_TREE, DATA_SAVE_DIAG_TASK, DATA_GET_HOST_INFO
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import MyResponse
from aops_utils.restful.helper import make_datacenter_url


def get_time_slices(time_range, interval):
    """
    split time range based on interval
    Args:
        time_range (list): time range of diagnose
        interval (int): diagnose time interval

    Returns:

    """
    time_points = [*range(time_range[0], time_range[1], interval), time_range[1]]
    time_slices = [[time_points[index-1], time_points[index]]
                   for index in range(1, len(time_points))]
    return time_slices


def get_validate_hosts(host_list, user_name):
    """
    get validate hosts
    Args:
        host_list (list): list of host ip
        user_name (str): user name

    Returns:
        list
    """
    host_info_url = make_datacenter_url(DATA_GET_HOST_INFO)
    pyload = {"username": user_name, "host_list": host_list, "basic": True}

    response = MyResponse.get_response("POST", host_info_url, pyload)
    if response["code"] != SUCCEED:
        LOGGER.error("Request to get validate hosts from database failed. %s" % response["msg"])
        return []

    LOGGER.info("Request validate hosts %s from database succeed." % host_list)

    validate_hosts = []
    host_infos = response["host_infos"]
    for host_info in host_infos:
        validate_hosts.append(host_info["host_id"])

    invalidate_hosts = list(set(host_list).difference(set(validate_hosts)))

    if invalidate_hosts:
        LOGGER.error("Host %s not found in database." % ", ".join(invalidate_hosts))

    return validate_hosts


def get_trees_content(tree_list, username):
    """
    get trees' content from database
    Args:
        tree_list (list): trees' names list
        username (str): user name

    Returns:
        dict
    """
    tree_dict = {}
    for tree_name in tree_list:
        tree_content = get_tree_from_database(username, tree_name)
        if tree_content:
            tree_dict[tree_name] = tree_content
        # Normally trees in database are all validate and user can only choose the
        # validated trees from website. In case of some strange situations, add debug log.
        else:
            LOGGER.debug("Diagnose tree %s content is none." % tree_name)

    return tree_dict


def get_tree_from_database(user_name, tree_name):
    """
    get tree content from database
    Args:
        user_name (str): user name
        tree_name (str): diagnose tree's name

    Returns:
        dict: diagnosed tree's dict
    """
    tree_dict = {}

    diag_tree_url = make_datacenter_url(DATA_GET_DIAG_TREE)
    pyload = {"username": user_name, "tree_list": [tree_name]}

    response = MyResponse.get_response("POST", diag_tree_url, pyload)
    if response["code"] != SUCCEED:
        LOGGER.error("Request to get tree from database failed. %s" % response["msg"])
        return tree_dict

    LOGGER.info("Request diag tree %s from database succeed." % tree_name)

    try:
        tree_dict = response["trees"][0]["tree_content"]
    except IndexError:
        LOGGER.error("The tree %s is not in database." % tree_name)
    except KeyError as error:
        LOGGER.error("Parsing tree content failed. %s is not found." % error)

    return tree_dict


def save_task(basic_args, task_id, report_num):
    """
    save task info into database
    Args:
        basic_args (dict): basic arguments from requests.
        e.g.:
            {
                "username": "admin",
                "host_list": ["host1", "host2"],
                "time_range": [ts1, ts2],
                "tree_list": ["tree1", "tree2"],
                "interval": 60
            }
        task_id (str): task id
        report_num (int): reports number

    Returns:
        None
    """
    pyload = {
        "username": basic_args["username"],
        "task_id": task_id,
        "time": int(time.time()),
        "host_list": basic_args["host_list"],
        "tree_list": basic_args["tree_list"],
        "time_range": basic_args["time_range"],
        "expected_report_num": report_num
    }
    save_task_url = make_datacenter_url(DATA_SAVE_DIAG_TASK)
    response = MyResponse.get_response("POST", save_task_url, pyload)

    if response["code"] != SUCCEED:
        LOGGER.error("Save task info %s into database failed. %s" %
                     (str(pyload), response["msg"]))
        return

    LOGGER.info("Save task info %s into database succeed." % str(pyload))
