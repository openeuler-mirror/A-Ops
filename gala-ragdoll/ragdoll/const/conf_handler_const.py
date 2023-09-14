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
@FileName: conf_handler_const.py
@Time: 2023/7/26 15:24
@Author: JiaoSiMao
Description:
"""
import re

NOT_SYNCHRONIZE = "NOT SYNCHRONIZE"
SYNCHRONIZED = "SYNCHRONIZED"
LIMITS_DOMAIN_RE = re.compile('(^[*]$)|(^[@|0-9A-Za-z]+[0-9A-Za-z]$)')
LIMITS_TYPE_VALUE = "soft|hard|-|"
LIMITS_ITEM_VALUE = "core|data|fsize|memlock|nofile|rss|stack|cpu|nproc|as|maxlogins|" \
                    "maxsyslogins|priority|locks|sigpending|" \
                    "msgqueue|nice|rtprio|"
RESOLV_KEY_VALUE = "nameserver|domain|search|sortlist|"
FSTAB_COLUMN_NUM = 6
