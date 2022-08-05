#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
from aops_check.conf.constant import (
    QUERY_APP,
    QUERY_APP_LIST,
    CREATE_APP
)
from aops_check.controllers import app_controller

URLS = []

SPECIFIC_URLS = {
    'APP_URLS': [
        (app_controller.CreateApp, CREATE_APP),
        (app_controller.QueryApp, QUERY_APP),
        (app_controller.QueryAppList, QUERY_APP_LIST)
    ]
}

for _, value in SPECIFIC_URLS.items():
    URLS.extend(value)
