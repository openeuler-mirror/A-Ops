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
Description: url set
"""
from aops_database.views.account import ChangePassword, Login
from aops_database.views.host import AddHost, DeleteHost, DeleteHostInfo, GetHost, AddHostGroup,\
    DeleteHostGroup, GetHostGroup, GetHostInfo, GetHostInfoByUser, SaveHostInfo, GetHostCount
from aops_database.views.deploy import AddTemplate, DeleteTemplate, GetTemplate, AddTask,\
    DeleteTask, GetTask
from aops_utils.conf.constant import DATA_ADD_HOST, DATA_DELETE_HOST, DATA_GET_HOST,\
    DATA_ADD_GROUP, DATA_DELETE_GROUP, DATA_GET_GROUP, DATA_GET_HOST_COUNT,\
    DATA_GET_HOST_INFO, DATA_SAVE_HOST_INFO, DATA_DELETE_HOST_INFO, DATA_GET_HOST_INFO_BY_USER,\
    DATA_ADD_TEMPLATE, DATA_DELETE_TEMPLATE, DATA_GET_TEMPLATE,\
    DATA_ADD_TASK, DATA_DELETE_TASK, DATA_GET_TASK,\
    DATA_GET_DIAG_TREE, DATA_ADD_DIAG_TREE, DATA_DELETE_DIAG_TREE,\
    DATA_GET_DIAG_REPORT, DATA_SAVE_DIAG_REPORT, DATA_DELETE_DIAG_REPORT,\
    DATA_GET_DIAG_REPORT_LIST, DATA_GET_DIAG_PROCESS,\
    DATA_ADD_CHECK_RULE, DATA_DELETE_CHECK_RULE, DATA_GET_CHECK_RULE, DATA_GET_CHECK_RULE_COUNT,\
    DATA_SAVE_CHECK_RESULT, DATA_DELETE_CHECK_RESULT, DATA_GET_CHECK_RESULT,\
    DATA_GET_CHECK_RESULT_COUNT, DATA_USER_LOGIN, DATA_USER_CHANGEPASSWORD,\
    DATA_GET_DATA

URLS = []

SPECIFIC_URLS = {
    "ACCOUNT_URLS": [
        (Login, DATA_USER_LOGIN),
        (ChangePassword, DATA_USER_CHANGEPASSWORD)
    ],
    "HOST_URLS": [
        (AddHost, DATA_ADD_HOST),
        (DeleteHost, DATA_DELETE_HOST),
        (GetHost, DATA_GET_HOST),
        (GetHostCount, DATA_GET_HOST_COUNT)
    ],
    "HOST_GROUP_URLS": [
        (AddHostGroup, DATA_ADD_GROUP),
        (DeleteHostGroup, DATA_DELETE_GROUP),
        (GetHostGroup, DATA_GET_GROUP)
    ],
    "HOST_INFO_URLS": [
        (GetHostInfo, DATA_GET_HOST_INFO),
        (SaveHostInfo, DATA_SAVE_HOST_INFO),
        (DeleteHostInfo, DATA_DELETE_HOST_INFO),
        (GetHostInfoByUser, DATA_GET_HOST_INFO_BY_USER)
    ],
    "TEMPLATE_URLS": [
        (AddTemplate, DATA_ADD_TEMPLATE),
        (DeleteTemplate, DATA_DELETE_TEMPLATE),
        (GetTemplate, DATA_GET_TEMPLATE)
    ],
    "TASK_URLS": [
        (AddTask, DATA_ADD_TASK),
        (DeleteTask, DATA_DELETE_TASK),
        (GetTask, DATA_GET_TASK)
    ]
}

for _, value in SPECIFIC_URLS.items():
    URLS.extend(value)
