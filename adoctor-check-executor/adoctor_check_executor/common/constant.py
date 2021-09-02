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
docs: constant.py
description: constant of check
"""
from dataclasses import dataclass

MAIN_DATA_MACRO = "$0"


@dataclass
class CheckTopic:
    """
    Check topic
    """
    import_check_rule_topic = "IMPORT_CHECK_RULE_TOPIC"
    delete_check_rule_topic = "DELETE_CHECK_RULE_TOPIC"
    do_check_topic = "DO_CHECK_TOPIC"
    retry_check_topic = "RETRY_CHECK_TOPIC"


@dataclass
class CheckGroup:
    """
    Check topic group
    """
    do_check_group_id = "DO_CHECK_GROUP_ID"
    import_check_rule_group_id = "IMPORT_CHECK_RULE_GROUP_ID"
    delete_check_rule_group_id = "DELETE_CHECK_RULE_GROUP_ID"
    retry_check_group_id = "RETRY_CHECK_GROUP_ID"


@dataclass
class CheckResultType:
    """
    Check result type
    """
    normal = "Normal"
    abnormal = "Abnormal"
    nodata = "No data"
    internal_error = "Internal error"
