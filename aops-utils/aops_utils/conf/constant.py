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
Description: config constant
"""
import os

BASE_CONFIG_PATH = '/etc/aops'

# path of global configuration
SYSTEM_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'system.ini')

# path of proxy configuration
MANAGER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'manager.ini')

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

# url format
URL_FORMAT = "http://%s:%s%s"

# manager route
ADD_HOST = "/manage/host/add"
DELETE_HOST = "/manage/host/delete"
QUERY_HOST = "/manage/host/get"
GET_HOST_COUNT = "/manage/host/count"

QUERY_HOST_DETAIL = "/manage/host/info/query"
HOST_SCENE_GET = '/manage/host/scene/get'

ADD_GROUP = "/manage/host/group/add"
DELETE_GROUP = "/manage/host/group/delete"
GET_GROUP = "/manage/host/group/get"

IMPORT_TEMPLATE = "/manage/template/import"
DELETE_TEMPLATE = "/manage/template/delete"
GET_TEMPLATE = "/manage/template/get"

EXECUTE_TASK = "/manage/task/execute"
DELETE_TASK = "/manage/task/delete"
GENERATE_TASK = "/manage/task/generate"
GET_TASK = "/manage/task/get"

COLLECT_CONFIG = '/manage/config/collect'

USER_LOGIN = "/manage/account/login"
USER_CERTIFICATE = "/manage/account/certificate"
CHANGE_PASSWORD = '/manage/account/change'
ADD_USER = '/manage/account/add'

AGENT_PLUGIN_INFO = '/manage/agent/plugin/info'
AGENT_PLUGIN_SET = '/manage/agent/plugin/set'
AGENT_METRIC_SET = '/manage/agent/metric/set'

# database route
DATA_ADD_HOST = "/data/host/add"
DATA_DELETE_HOST = "/data/host/delete"
DATA_GET_HOST = "/data/host/get"
DATA_GET_HOST_COUNT = "/data/host/count"

DATA_ADD_GROUP = "/data/host/group/add"
DATA_DELETE_GROUP = "/data/host/group/delete"
DATA_GET_GROUP = "/data/host/group/get"

DATA_GET_HOST_INFO = "/data/host/info/get"
DATA_GET_HOST_INFO_BY_USER = "/data/host/info/get/user"
DATA_DELETE_HOST_INFO = "/data/host/info/delete"
DATA_SAVE_HOST_INFO = "/data/host/info/save"

DATA_GET_DATA = "/data/data/get"

DATA_ADD_TEMPLATE = "/data/manage/template/add"
DATA_DELETE_TEMPLATE = "/data/manage/template/delete"
DATA_GET_TEMPLATE = "/data/manage/template/get"

DATA_ADD_TASK = "/data/manage/task/add"
DATA_DELETE_TASK = "/data/manage/task/delete"
DATA_GET_TASK = "/data/manage/task/get"

DATA_ADD_DIAG_TREE = "/data/diag/tree/add"
DATA_DELETE_DIAG_TREE = "/data/diag/tree/delete"
DATA_GET_DIAG_TREE = "/data/diag/tree/get"
DATA_SAVE_DIAG_REPORT = "/data/diag/report/save"
DATA_DELETE_DIAG_REPORT = "/data/diag/report/delete"
DATA_GET_DIAG_REPORT = "/data/diag/report/get"
DATA_GET_DIAG_REPORT_LIST = "/data/diag/report/get_list"
DATA_GET_DIAG_PROCESS = "/data/diag/process/query"
DATA_SAVE_DIAG_TASK = "/data/diag/task/save"
DATA_GET_DIAG_TASK = "/data/diag/task/get"

DATA_ADD_CHECK_RULE = "/data/check/rule/add"
DATA_DELETE_CHECK_RULE = "/data/check/rule/delete"
DATA_GET_CHECK_RULE = "/data/check/rule/get"
DATA_GET_CHECK_RULE_COUNT = "/data/check/rule/count"
DATA_SAVE_CHECK_RESULT = "/data/check/result/save"
DATA_DELETE_CHECK_RESULT = "/data/check/result/delete"
DATA_GET_CHECK_RESULT = "/data/check/result/get"
DATA_GET_CHECK_RESULT_COUNT = "/data/check/result/count"

DATA_USER_LOGIN = "/data/account/login"
DATA_USER_CHANGE_PASSWORD = "/data/account/change"

# diagnose route
DIAG_IMPORT_TREE = "/diag/tree/import"
DIAG_GET_TREE = "/diag/tree/get"
DIAG_DELETE_TREE = "/diag/tree/delete"
DIAG_GET_TASK = "/diag/task/get"
DIAG_GET_REPORT = "/diag/report/get"
DIAG_GET_REPORT_LIST = "/diag/report/get_list"
DIAG_DELETE_REPORT = "/diag/report/delete"
DIAG_EXECUTE_DIAG = "/diag/execute"
DIAG_GET_PROGRESS = "/diag/progress/get"

# check route
CHECK_GET_RESULT = "/check/result/get"
CHECK_COUNT_RESULT = "/check/result/count"
CHECK_GET_RULE = "/check/rule/get"
CHECK_IMPORT_RULE = "/check/rule/import"
CHECK_DELETE_RULE = "/check/rule/delete"
CHECK_COUNT_RULE = "/check/rule/count"

# parameter
MAX_PORT = 65535
MIN_PORT = 0
