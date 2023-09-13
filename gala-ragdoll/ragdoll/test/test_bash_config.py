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
@FileName: test_bash_config.py
@Time: 2023/9/04 10:08
@Author: JiaoSiMao
Description:
"""
from __future__ import absolute_import
import importlib
import json

from ragdoll.config_model.bash_config import BashConfig
from ragdoll.test import BaseTestCase
from ragdoll.const.conf_handler_const import SYNCHRONIZED, NOT_SYNCHRONIZE

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
PROJECT_NAME = "_config"
CONF_TYPE = "bash"

CONF_INFO = "#!/bin/bash\n" \
            "touch /var/lock/subsys/local"
NOT_SYNCHRONIZE_CONF = '[\n' \
                       '"#!/bin/bash", \n' \
                       '"touch /var/lock/subsys/local",\n' \
                       '"touch /var/log/test"\n' \
                       ']'
SYNCHRONIZE_CONF = '[\n' \
                   '"#!/bin/bash", \n' \
                   '"touch /var/lock/subsys/local"\n' \
                   ']'

NULL_CONF_INFO = ""


class TestBashConfig(BaseTestCase):
    def create_conf_model(self):
        conf_model = ""
        project_name = CONF_TYPE + PROJECT_NAME  # example: ini_config
        project_path = BASE_PATH + project_name  # example: ragdoll.config_model.ini_config
        model_name = CONF_TYPE.capitalize() + CONFIG_MODEL_NAME  # example: IniConfig

        try:
            project = importlib.import_module(project_path)
        except ImportError:
            conf_model = ""
        else:
            _conf_model_class = getattr(project, model_name, None)  # example: IniConfig
            if _conf_model_class:
                conf_model = _conf_model_class()  # example: IniConfig()

        return conf_model

    def test_parse_conf_to_dict(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        self.assertEqual(len(conf_dict_list), 2)

    def test_read_conf_null(self):
        conf_model = self.create_conf_model()
        conf_model.read_conf(NULL_CONF_INFO)
        self.assertEqual(len(conf_model.conf), 0)

    def test_conf_compare(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        res = conf_model.conf_compare(NOT_SYNCHRONIZE_CONF, json.dumps(conf_dict_list))
        self.assertEqual(res, NOT_SYNCHRONIZE)

        res = conf_model.conf_compare(SYNCHRONIZE_CONF, json.dumps(conf_dict_list))
        self.assertEqual(res, SYNCHRONIZED)

    def test_write_conf(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        bash_config = BashConfig()
        bash_config.conf = conf_dict_list
        content = conf_model.write_conf()
        self.assertTrue(len(content) > 0)


if __name__ == '__main__':
    import unittest

    unittest.main()
