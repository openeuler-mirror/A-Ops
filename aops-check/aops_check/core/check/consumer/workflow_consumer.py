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
from aops_utils.log.log import LOGGER

from aops_check.core.check.consumer import Consumer
from aops_check.core.rule.workflow import Workflow


class WorkflowConsumer(Consumer):
    def _process_msgs(self, msg):
        LOGGER.debug("msg: %s", msg)
        workflow_id = msg.get('workflow_id')
        username = msg.get('username')
        time_range = msg.get('time_range')
        workflow = Workflow(username, workflow_id)
        workflow.execute(time_range)
