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
Date: 2021/8/4 17:20
docs: check_executor_manager.py
description: manager of check executor
"""
import sys
from adoctor_check_executor.common.config import executor_check_config
from adoctor_check_executor.common.check_consumer import ImportRuleConsumer, \
    DelRuleConsumer, DoCheckConsumer
from adoctor_check_executor.check_executor.check_item_manager import check_item_manager
from adoctor_check_executor.common.constant import CheckTopic, CheckGroup

consumer_thread_list = []


def start_check_executor():
    """
    Check service manager.
    """
    check_item_manager.query_check_rule()
    import_rule_consumer = ImportRuleConsumer(CheckTopic.import_check_rule_topic,
                                              CheckGroup.import_check_rule_group_id,
                                              executor_check_config)
    consumer_thread_list.append(import_rule_consumer)
    import_rule_consumer.start()

    delete_rule_consumer = DelRuleConsumer(CheckTopic.delete_check_rule_topic,
                                           CheckGroup.delete_check_rule_group_id,
                                           executor_check_config)
    consumer_thread_list.append(delete_rule_consumer)
    delete_rule_consumer.start()

    consumer_num = int(executor_check_config.executor.get("DO_CHECK_CONSUMER_NUM"))
    while consumer_num > 0:
        do_check_consumer = DoCheckConsumer(CheckTopic.do_check_topic,
                                            CheckGroup.do_check_group_id,
                                            executor_check_config)
        consumer_thread_list.append(do_check_consumer)
        do_check_consumer.start()
        consumer_num -= 1


def stop_check_scheduler():
    """
    Stop check executor
    """
    for consumer in consumer_thread_list:
        consumer.stop_consumer()


def main():
    """
    Main function.
    """
    command = sys.argv[1]
    if command == "start":
        start_check_executor()
    elif command == "stop":
        stop_check_scheduler()
    else:
        print("Invalid parameter")


if __name__ == "__main__":
    main()
