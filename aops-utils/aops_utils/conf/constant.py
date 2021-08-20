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
Description: constant
"""
import os

BASE_CONFIG_PATH = '/etc/aops'

# path of global configuration
SYSTEM_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'system.ini')

# url format
URL_FORMAT = "http://%s:%s%s"

# manager route
ADD_HOST = "/manage/host/add"
DELETE_HOST = "/manage/host/delete"
QUERY_HOST = "/manage/host/get"
GET_HOST_COUNT = "/manage/host/count"

QUERY_HOST_DETAIL = "/manage/host/info/query"

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
CHANGE_PASSSWORD = '/manage/account/change'


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

DATA_ADD_CHECK_RULE = "/data/check/rule/add"
DATA_DELETE_CHECK_RULE = "/data/check/rule/delete"
DATA_GET_CHECK_RULE = "/data/check/rule/get"
DATA_GET_CHECK_RULE_COUNT = "/data/check/rule/count"
DATA_SAVE_CHECK_RESULT = "/data/check/result/save"
DATA_DELETE_CHECK_RESULT = "/data/check/result/delete"
DATA_GET_CHECK_RESULT = "/data/check/result/get"
DATA_GET_CHECK_RESULT_COUNT = "/data/check/result/count"

DATA_USER_LOGIN = "/data/account/login"
DATA_USER_CHANGEPASSWORD = "/data/acount/change"

# parameter
MAX_PORT = 65535
MIN_PORT = 0
