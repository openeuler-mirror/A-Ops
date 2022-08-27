#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
from typing import NoReturn

from aops_utils.log.log import LOGGER

from aops_check.conf import configuration
from aops_check.core.check.consumer import ConsumerManager
from aops_check.core.check.consumer.workflow_consumer import WorkflowConsumer
from aops_check.mode import mode, Mode


@mode.register('executor')
class Executor(Mode):
    """
    It's a executor which just does check.
    """

    @property
    def name(self) -> str:
        return "executor"

    @staticmethod
    def run() -> NoReturn:
        consumer_list = [
            WorkflowConsumer(configuration.consumer.get('TASK_NAME'),
                             configuration.consumer.get('TASK_GROUP_ID'),
                             configuration)
        ]
        manager = ConsumerManager(consumer_list)
        manager.run()
        LOGGER.info("check executor start succeed")
