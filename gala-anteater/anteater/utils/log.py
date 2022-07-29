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
Time:
Author:
Description: the implementation of logging
"""

import os
import logging.config
import logging


class Log(object):
    __flag = None

    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        log_path = os.getcwd() + os.sep + "logs"
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        log_file_path = os.path.join(root_path, "configuration" + os.sep + "log.settings.ini")
        if not os.path.isfile(log_file_path):
            raise FileExistsError("log.settings.ini was not found!")

        logging.config.fileConfig(log_file_path)
        self.logger = logging.getLogger()

    def get_logger(self):
        return self.logger
