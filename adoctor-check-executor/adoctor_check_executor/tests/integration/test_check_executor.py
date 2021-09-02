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
Date: 2021/9/1 23:04
docs: test_executor.py
description: test executor
"""
import os
import sys
import json
from adoctor_check_scheduler.common.constant import CheckTopic, CheckGroup
from adoctor_check_scheduler.common.config import scheduler_check_config
from adoctor_check_scheduler.common.check_consumer import RetryTaskConsumer
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError
from aops_utils.log.log import LOGGER

CONFIG_PATH = "conf"


def publish_check_task(task_msg):
    """
    Publish check task
    Args:
        task_msg (dict): task msg
    """
    try:
        producer = BaseProducer(scheduler_check_config)
        LOGGER.debug("Send check task msg %s", task_msg)
        producer.send_msg(CheckTopic.do_check_topic, task_msg)
    except ProducerInitError as exp:
        LOGGER.error("Produce task msg failed. %s" % exp)


def test_do_check():
    test_msg = {'task_id': 1630421641844, 'user': 'admin',
                'host_list': [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                               'public_ip': '90.90.64.65'}],
                'check_items': ['check_item2'], 'time_range': [1630421611, 1630421641]}

    publish_check_task(test_msg)


def test_import_check_rule():
    config_path = os.path.join(CONFIG_PATH, "check_rule.json")
    with open(config_path, 'r', encoding='utf-8-sig') as cfg_file:
        check_config = json.load(cfg_file)
    check_config["username"] = "admin"
    publish_check_task(check_config)


def test_delete_check_rule():
    delete_check_msg = {
        "user": "admin",
        "check_items": ["check_item1", "check_item7"]
    }
    publish_check_task(delete_check_msg)


def start_retry_consumer():
    # Start retry task consumer
    retry_task_consumer = RetryTaskConsumer(CheckTopic.retry_check_topic,
                                            CheckGroup.retry_check_group_id,
                                            scheduler_check_config)
    retry_task_consumer.start()
    retry_task_consumer.join()


test_func = {"import_check_rule": test_import_check_rule,
             "delete_check_rule": test_delete_check_rule,
             "do_check": test_do_check,
             "start_retry_consumer": start_retry_consumer
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
