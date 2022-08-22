#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import os

agent = {
    "IP": "127.0.0.1",
    "PORT": 12000
}

gopher = {
    "CONFIG_PATH": "/opt/gala-gopher/gala-gopher.conf"
}

log = {
    "LOG_DIR": os.path.join('/', 'var', 'log', 'aops'),
    "LOG_LEVEL": 'INFO',
    "MAX_BYTES": 31457280,
    "BACKUP_COUNT": 30
}
