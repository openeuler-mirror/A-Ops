#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/22 22:39
docs: test_check_rule.py
description: test_check
"""
import os
import json
import sys
import requests
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER
from adoctor_check_scheduler.common.constant import CheckTopic
from adoctor_check_scheduler.common.config import scheduler_check_config

CONFIG_PATH = "conf"
SCHEDULER_URL = "http://127.0.0.1:60116"


def send_msg(method, url, data):
    """
    Send update config request
    Args:
        data: parameters

    Returns:
        response in str

    """
    header = {
        "Content-Type": "application/json; charset=UTF-8",
        "access_token": "81ef"
    }
    response = requests.request(
        method, url, data=json.dumps(data), headers=header)
    print(response.status_code)
    print(response)
    print(json.dumps(response.json(), indent=2))
    return response.json()


def test_import_check_rule():
    """
    Test update config
    Returns:
        Non

    """
    config_path = os.path.join(CONFIG_PATH, "check_rule.json")
    with open(config_path, 'r', encoding='utf-8-sig') as cfg_file:
        check_config = json.load(cfg_file)

    print(check_config)
    send_msg('POST', SCHEDULER_URL + '/check/rule/import', check_config)


def test_delete_check_rule():
    """
    Test update config
    Returns:
        Non

    """
    delete_check_msg = {
        "check_items": ["check_item1", "check_item7"]
    }
    send_msg('DELETE', SCHEDULER_URL + '/check/rule/delete', delete_check_msg)


def test_get_check_rule():
    """
    Test update config
    Returns:
        Non

    """
    get_check_msg = {
        "check_items": ["check_item1", "check_item7"],
        "page": 1,
        "per_page": 50
    }
    send_msg('POST', SCHEDULER_URL + '/check/rule/get', get_check_msg)


def test_get_check_rule_count():
    """
    Test update config
    Returns:
        Non

    """
    send_msg('POST', SCHEDULER_URL + '/check/rule/count', {})


def test_get_check_result():
    """
    Test update config
    Returns:
        Non

    """
    get_check_result_msg = {
        "time_range": [1630050000, 1630056585],
        "check_items": ["check_item1", "check_item7"],
        "host_list": [],
        "page": 1,
        "per_page": 50
    }
    send_msg('POST', SCHEDULER_URL + '/check/result/get', get_check_result_msg)


def test_add_retry_task():
    test_msg = {'task_id': 1630421641844, 'user': 'admin',
                'host_list': [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                               'public_ip': '90.90.64.65'}],
                'check_items': ['check_item2'], 'time_range': [1630421611, 1630421641]}
    try:
        producer = BaseProducer(scheduler_check_config)
        LOGGER.debug("Send check task msg %s", test_msg)
        producer.send_msg(CheckTopic.do_check_topic, test_msg)
    except ProducerInitError as exp:
        LOGGER.error("Produce task msg failed. %s" % exp)


test_func = {"import_check_rule": test_import_check_rule,
             "delete_check_rule": test_delete_check_rule,
             "get_check_rule": test_get_check_rule,
             "get_check_rule_count": test_get_check_rule_count,
             "get_check_result": test_get_check_result,
             "add_retry_task": test_add_retry_task
             }


def main():
    """
    Entry of commands.
    """
    if len(sys.argv) != 2:
        LOGGER.error("Invalid parameter. Available options are "
                     "as follows:[diag,check_default,check_user]")
        return
    test_mode = sys.argv[1]
    if test_mode in test_func.keys():
        test_func[test_mode]()
    else:
        LOGGER.error("Invalid test mode %s. Available options are "
                     "as follows:[diag,check_default,check_user]",
                     sys.argv[1])


if __name__ == '__main__':
    main()
