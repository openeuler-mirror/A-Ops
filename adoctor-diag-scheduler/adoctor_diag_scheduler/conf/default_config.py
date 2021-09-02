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
    "kafka_server_list": "90.90.64.64:9092",
    "api_version": "0.11.5",
    "acks": 1,
    "retries": 3,
    "retry_backoff_ms": 100
}


topic = {
    "name": "DIAGNOSE_EXECUTE_REQ"
}


diag_scheduler = {
    "ip": "127.0.0.1",
    "port": 60116
}
