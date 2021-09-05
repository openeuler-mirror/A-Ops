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
from aops_manager.host_manager import view as host_view
from aops_manager.deploy_manager import view as deploy_view
from aops_manager.config_manager import view as config_view
from aops_manager.account_manager import view as account_view
from aops_utils.conf.constant import ADD_HOST, DELETE_HOST, GET_HOST_COUNT,\
    QUERY_HOST, QUERY_HOST_DETAIL, ADD_GROUP, DELETE_GROUP, GET_GROUP,\
    GENERATE_TASK, DELETE_TASK, EXECUTE_TASK, GET_TASK,\
    IMPORT_TEMPLATE, DELETE_TEMPLATE, GET_TEMPLATE,\
    COLLECT_CONFIG, USER_LOGIN, USER_CERTIFICATE, CHANGE_PASSSWORD

URLS = []

SPECIFIC_URLS = {
    "ACCOUNT_URLS": [
        (account_view.Login, USER_LOGIN),
        (account_view.Certificate, USER_CERTIFICATE),
        (account_view.ChangePassword, CHANGE_PASSSWORD)
    ],
    "HOST_URLS": [
        (host_view.AddHost, ADD_HOST),
        (host_view.DeleteHost, DELETE_HOST),
        (host_view.GetHost, QUERY_HOST),
        (host_view.GetHostInfo, QUERY_HOST_DETAIL),
        (host_view.GetHostCount, GET_HOST_COUNT)
    ],
    "HOST_GROUP_URLS": [
        (host_view.AddHostGroup, ADD_GROUP),
        (host_view.DeleteHostGroup, DELETE_GROUP),
        (host_view.GetHostGroup, GET_GROUP)
    ],
    "TEMPLATE_URLS": [
        (deploy_view.ImportTemplate, IMPORT_TEMPLATE),
        (deploy_view.DeleteTemplate, DELETE_TEMPLATE),
        (deploy_view.GetTemplate, GET_TEMPLATE)
    ],
    "TASK_URLS": [
        (deploy_view.GenerateTask, GENERATE_TASK),
        (deploy_view.DeleteTask, DELETE_TASK),
        (deploy_view.ExecuteTask, EXECUTE_TASK),
        (deploy_view.GetTask, GET_TASK),
    ],
    "CONFIG_URLS": [
        (config_view.CollectConfig, COLLECT_CONFIG)
    ]
}

for _, value in SPECIFIC_URLS.items():
    URLS.extend(value)
