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
import threading
import json
from typing import NoReturn

from aops_agent.conf.constant import DEFAULT_TOKEN_PATH

global TOKEN


class TokenManage:
    mutex = threading.Lock()

    @classmethod
    def init(cls) -> NoReturn:
        """
            init global var _TOKEN
        """
        global TOKEN
        TokenManage.mutex.acquire()
        try:
            with open(DEFAULT_TOKEN_PATH, "r") as f:
                row_data = json.load(f)
                TOKEN = row_data.get('access_token', '')
        except FileNotFoundError:
            TOKEN = ''
        TokenManage.mutex.release()

    @classmethod
    def set_value(cls, value: str) -> NoReturn:
        """
            update _TOKEN
        Args:
            value: token string
        """
        global TOKEN
        TokenManage.mutex.acquire()
        TOKEN = value
        TokenManage.mutex.release()

    @classmethod
    def get_value(cls) -> str:
        """
            get token
        """
        TokenManage.mutex.acquire()
        token = TOKEN
        TokenManage.mutex.release()
        return token
