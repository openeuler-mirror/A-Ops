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
Description: default config
"""
check = {
    "IP": "127.0.0.1",
    "PORT": 11112,
    "MODE": "configurable",
    "TIMING_CHECK": "on"
}

mysql = {
    "IP": "127.0.0.1",
    "PORT": 3306,
    "DATABASE_NAME": "aops",
    "ENGINE_FORMAT": "mysql+pymysql://@%s:%s/%s",
    "POOL_SIZE": 10000,
    "POOL_RECYCLE": 7200
}

elasticsearch = {
    "IP": "127.0.0.1",
    "PORT": 9200
}

prometheus = {
    "IP": "127.0.0.1",
    "PORT": 9090,
    "QUERY_RANGE_STEP" : "15s"
}

agent = {
    "DEFAULT_INSTANCE_PORT": 8888
}

manager = {
    "IP": "127.0.0.1",
    "PORT": 11111
}

consumer = {
    "KAFKA_SERVER_LIST": "127.0.0.1:9092",
    "ENABLE_AUTO_COMMIT": False,
    "AUTO_OFFSET_RESET": "earliest",
    "TIMEOUT_MS": 5,
    "MAX_RECORDS": 3,
    "TASK_NAME": "CHECK_TASK",
    "TASK_GROUP_ID": "CHECK_TASK_GROUP_ID",
    "RESULT_NAME": "CHECK_RESULT"
}

producer = {
    "KAFKA_SERVER_LIST": "127.0.0.1:9092",
    "API_VERSION": "0.11.5",
    "ACKS": 1,
    "RETRIES": 3,
    "RETRY_BACKOFF_MS": 100,
    "TASK_NAME": "CHECK_TASK",
    "TASK_GROUP_ID": "CHECK_TASK_GROUP_ID"
}
