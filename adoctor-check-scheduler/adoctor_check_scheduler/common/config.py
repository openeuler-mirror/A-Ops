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
Author: YangYunYi
Date: 2021/8/4 17:20
docs: config.py
description: config of check scheduler
"""
import os
from aops_utils.conf import Config
from aops_utils.conf.constant import BASE_CONFIG_PATH

# Configuration file path
CHECK_SCHEDULER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'check_scheduler.ini')
scheduler_check_config = Config(CHECK_SCHEDULER_CONFIG_PATH)
