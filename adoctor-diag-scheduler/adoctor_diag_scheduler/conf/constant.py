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
Description: diagnose scheduler constant
"""
import os
from aops_utils.conf.constant import BASE_CONFIG_PATH
from aops_utils.conf import configuration

# diagnose scheduler config
SCHEDULER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'diag_scheduler.ini')
DATABASE_IP = configuration.database.get("IP")
DATABASE_PORT = configuration.database.get("PORT")
