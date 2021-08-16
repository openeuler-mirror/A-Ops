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
'''
Time:
Author:
Description:
'''
import os
import unittest

from aops.utils.conf import Config
from .for_test_conf import global_config
from aops.utils.compare import compare_two_object


class TestConf(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.abspath(os.path.dirname(__file__))

    def test_conf_read(self):
        config_path = os.path.join(self.config_dir, 'for_test_conf/config.ini')
        conf = Config(config_path, global_config)
        config = [
            {
                "TEST1": 3,
                "TEST2": 2,
                "TEST3": 4
            },
            {
                "A": 1,
                "B": 2,
                "C": True
            }
        ]

        self.assertTrue(compare_two_object(config[0], conf.test))
        self.assertTrue(compare_two_object(config[1], conf.test2))
