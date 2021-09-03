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
Date: 2021/8/23 20:20
docs: __init__.py
description: Add view and url into api
"""
from adoctor_check_scheduler import view
from aops_utils.conf.constant import CHECK_GET_RESULT, CHECK_COUNT_RESULT, \
    CHECK_GET_RULE, CHECK_IMPORT_RULE, CHECK_DELETE_RULE, CHECK_COUNT_RULE

urls = [
    (view.GetCheckResult, CHECK_GET_RESULT, ["POST"]),
    (view.GetCheckResultCount, CHECK_COUNT_RESULT, ["POST"]),
    (view.GetCheckRule, CHECK_GET_RULE, ["POST"]),
    (view.ImportCheckRule, CHECK_IMPORT_RULE, ["POST"]),
    (view.DeleteCheckRule, CHECK_DELETE_RULE, ["DELETE"]),
    (view.GetCheckRuleCount, CHECK_COUNT_RULE, ["POST"]),
]
