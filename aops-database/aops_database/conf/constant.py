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
Description: database constant
"""
import os
from aops_utils.conf.constant import BASE_CONFIG_PATH

# database config
DATABASE_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'database.ini')

HOST_INFO_INDEX = 'host_information'
TEMPLATE_INDEX = "ansible_templates"
TASK_INDEX = "ansible_task"
DATA_HISTORY = "history"
DATA_MESSAGES = "messages"
DIAG_REPORT_INDEX = "diag_report"
DIAG_TREE_INDEX = "diag_tree"
DIAG_TASK_INDEX = "diag_task"
CHECK_RESULT_INDEX = "check_result"
CHECK_RULE_INDEX = "check_rule"
