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
@FileName: test_kv_config.py
@Time: 2023/7/20 16:09
@Author: JiaoSiMao
Description: util test of kv_config
"""
from __future__ import absolute_import
import importlib
import json

from ragdoll.config_model.kv_config import KvConfig
from ragdoll.test import BaseTestCase
from ragdoll.const.conf_handler_const import NOT_SYNCHRONIZE, SYNCHRONIZED

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
PROJECT_NAME = "_config"
CONF_TYPE = "kv"

CONF_INFO = "# For more information about this file, see the ntp.conf(5) man page.\n" \
            "# Record the frequency of the system clock.\n" \
            "driftfile /var/lib/ntp/drift \n" \
            "# Permit time synchronization with our time source, but do not\n" \
            "# permit the source to query or modify the service on this system.\n" \
            "restrict default nomodify notrap nopeer noepeer noquery\n" \
            "# Permit association with pool servers.\n" \
            "restrict source nomodify notrap noepeer noquery\n" \
            "# Permit all access over the loopback interface.  This could\n" \
            "# be tightened as well, but to do so would effect some of\n" \
            "# the administrative functions.\n" \
            "restrict 127.0.0.1\n" \
            "restrict ::1\n" \
            "# Hosts on local network are less restricted. \n" \
            "# restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap \n" \
            "# Use public servers from the pool.ntp.org project. \n" \
            "# Please consider joining the pool (http://www.pool.ntp.org/join.html). \n" \
            "# pool 2.openEuler.pool.ntp.org iburst \n" \
            "# Reduce the maximum number of servers used from the pool. \n" \
            "tos maxclock 5 \n" \
            "# Enable public key cryptography. \n" \
            "# crypto \n" \
            "includefile /etc/ntp/crypto/pw \n" \
            "# Key file containing the keys and key identifiers used when operating \n" \
            "# with symmetric key cryptography. \n" \
            "keys /etc/ntp/keys \n" \
            "# Specify the key identifiers which are trusted. \n" \
            "# trustedkey 4 8 42 \n" \
            "# Specify the key identifier to use with the ntpdc utility. \n" \
            "# requestkey 8 \n" \
            "# Specify the key identifier to use with the ntpq utility. \n" \
            "# controlkey 8 \n" \
            "# Enable writing of statistics records. \n" \
            "# statistics clockstats cryptostats loopstats peerstats \n"

EQUAL_SPACER_CONF_INFO = "kernel.sysrq=0\n" \
                         "net.ipv4.ip_forward=0\n" \
                         "net.ipv4.conf.all.send_redirects=0\n" \
                         "kernel.dmesg_restrict=1\n" \
                         "net.ipv6.conf.default.accept_redirects=0\n"
NOT_SYNCHRONIZE_CONF = '[\n' \
                       '{\n' \
                       '"keys": "/etc/ntp/keys"\n' \
                       '}, \n' \
                       '{\n' \
                       '"statistics": "clockstats cryptostats loopstats peerstats"\n' \
                       '}' \
                       ']'
SYNCHRONIZE_CONF = '[\n' \
                   '{\n' \
                   '"driftfile": "/var/lib/ntp/drift"\n' \
                   '}, \n' \
                   '{\n' \
                   '"restrict": "default nomodify notrap nopeer noepeer noquery"\n' \
                   '},' \
                   '{\n' \
                   '"restrict": "source nomodify notrap noepeer noquery"\n' \
                   '},' \
                   '{\n' \
                   '"restrict": "127.0.0.1"\n' \
                   '},' \
                   '{\n' \
                   '"restrict": "::1"\n' \
                   '},' \
                   '{\n' \
                   '"tos": "maxclock 5"\n' \
                   '},' \
                   '{\n' \
                   '"includefile": "/etc/ntp/crypto/pw"\n' \
                   '},' \
                   '{\n' \
                   '"keys": "/etc/ntp/keys"\n' \
                   '}' \
                   ']'

NOT_SYNCHRONIZE_CONF_EQUAL = '[\n' \
                             '{\n' \
                             '"kernel.sysrq": "1"\n' \
                             '}, \n' \
                             '{\n' \
                             '"net.ipv4.ip_forward": "0"\n' \
                             '}' \
                             ']'
SYNCHRONIZE_CONF_EQUAL = '[\n' \
                         '{\n' \
                         '"kernel.sysrq": "0"\n' \
                         '}, \n' \
                         '{\n' \
                         '"net.ipv4.ip_forward": "0"\n' \
                         '},' \
                         '{\n' \
                         '"net.ipv4.conf.all.send_redirects": "0"\n' \
                         '},' \
                         '{\n' \
                         '"kernel.dmesg_restrict": "1"\n' \
                         '},' \
                         '{\n' \
                         '"net.ipv6.conf.default.accept_redirects": "0"\n' \
                         '}' \
                         ']'
NULL_CONF_INFO = ""


class TestSshdConfig(BaseTestCase):
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

    def test_parse_conf_to_dict_space_spacer(self):
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": ""}
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO, space_type, "openEuler-kv_config")
        self.assertEqual(len(conf_dict_list), 8)

    def test_parse_conf_to_dict_equal_spacer(self):
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": "="}
        conf_dict_list = conf_model.parse_conf_to_dict(EQUAL_SPACER_CONF_INFO, space_type, "openEuler-kv_config")
        self.assertEqual(len(conf_dict_list), 5)

    def test_read_conf_null(self):
        conf_model = self.create_conf_model()
        conf_model.read_conf(NULL_CONF_INFO)
        self.assertEqual(len(conf_model.conf), 0)

    def test_conf_compare_space(self):
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": ""}
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO, space_type, "openEuler-kv_config")
        res = conf_model.conf_compare(NOT_SYNCHRONIZE_CONF, json.dumps(conf_dict_list))
        self.assertEqual(res, NOT_SYNCHRONIZE)

        res = conf_model.conf_compare(SYNCHRONIZE_CONF, json.dumps(conf_dict_list))
        self.assertEqual(res, SYNCHRONIZED)

    def test_conf_compare_equal(self):
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": "="}
        conf_dict_list = conf_model.parse_conf_to_dict(EQUAL_SPACER_CONF_INFO, space_type, "openEuler-kv_config")
        res = conf_model.conf_compare(NOT_SYNCHRONIZE_CONF_EQUAL, json.dumps(conf_dict_list))
        self.assertEqual(res, NOT_SYNCHRONIZE)

        res = conf_model.conf_compare(SYNCHRONIZE_CONF_EQUAL, json.dumps(conf_dict_list))
        self.assertEqual(res, SYNCHRONIZED)

    def test_write_conf_space(self):
        kv_config = KvConfig()
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": ""}
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO, space_type, "openEuler-kv_config")
        kv_config.conf = conf_dict_list
        content = conf_model.write_conf(space_type={"openEuler-kv_config": ""}, yang_info="openEuler-kv_config")
        self.assertTrue(len(content) > 0)

    def test_write_conf_equal(self):
        kv_config = KvConfig()
        conf_model = self.create_conf_model()
        space_type = {"openEuler-kv_config": "="}
        conf_dict_list = conf_model.parse_conf_to_dict(EQUAL_SPACER_CONF_INFO, space_type, "openEuler-kv_config")
        kv_config.conf = conf_dict_list
        content = conf_model.write_conf(space_type={"openEuler-kv_config": "="}, yang_info="openEuler-kv_config")
        self.assertTrue(len(content) > 0)


if __name__ == '__main__':
    import unittest

    unittest.main()
