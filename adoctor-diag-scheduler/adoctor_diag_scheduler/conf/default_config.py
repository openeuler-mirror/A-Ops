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
Description: default config of database
"""
producer = {
    "KAFKA_SERVER_LIST": "90.90.64.64:9092",
    "API_VERSION": "0.11.5",
    "ACKS": 1,
    "RETRIES": 3,
    "RETRY_BACKOFF_MS": 100
}


topic = {
    "NAME": "DIAGNOSE_EXECUTE_REQ"
}


diag_scheduler = {
    "IP": "127.0.0.1",
    "PORT": 60116
}
