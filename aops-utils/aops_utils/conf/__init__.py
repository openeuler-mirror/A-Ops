#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: global config.
"""
import os
import configparser

from aops.utils.conf import default_config
from aops.utils.conf.constant import SYSTEM_CONFIG_PATH


class Config:
    """
    Merge system default configuration with configuration file.
    """

    def __init__(self, config_file, default=None):
        """
        Class instance initialization.

        Args:
            config_file(str): configuration file
            default(module): module of default configuration
        """
        # read default configuration
        if default is not None:
            for config in dir(default):
                setattr(self, config, getattr(default, config))

        self.read_config(config_file)

    def read_config(self, config_file):
        """
        read configuration from file.

        Args:
            config_file(str): configuration file
        """
        if not os.path.exists(config_file):
            return

        conf = configparser.RawConfigParser()
        try:
            conf.read(config_file)
        except configparser.ParsingError:
            return

        for section in conf.sections():
            temp_config = dict()
            for option in conf.items(section):
                try:
                    (key, value) = option
                except IndexError:
                    pass
                else:
                    if not value:
                        continue
                    if value.isdigit():
                        value = int(value)
                    elif value.lower() in ('true', 'false'):
                        value = (True if value.lower() == 'true' else False)
                    temp_config[key.upper()] = value
            if temp_config:
                # let default configuration be merged with configuration from config file
                if hasattr(self, section):
                    getattr(self, section).update(temp_config)
                else:
                    setattr(self, section, temp_config)


configuration = Config(SYSTEM_CONFIG_PATH, default_config)
