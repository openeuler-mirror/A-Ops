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
"""
Time:
Author:
Description: default config
"""
producer = {
    "KAFKA_SERVER_LIST": "127.0.0.1:9092",
    "API_VERSION": "0.11.5",
    "ACKS": 1,
    "RETRIES": 3,
    "RETRY_BACKOFF_MS": 100
}


topic = {
    "NAME": "CHECK_EXECUTE"
}


prometheus = {
    "IP": "127.0.0.1",
    "PORT": 9090,
    "QUERY_RANGE_STEP" : "15s"
}

agent = {
    "DEFAULT_INSTANCE_PORT": 9100
}