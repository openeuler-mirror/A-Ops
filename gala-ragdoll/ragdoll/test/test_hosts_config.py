# coding: utf-8

import importlib
import json

from ragdoll.test import BaseTestCase

CONFIG_TEXT = "   # Loopback entries; do not change.\n" \
              " # For historical reasons, localhost precedes localhost.localdomain:\n" \
              "127.0.0.1   localhost         localhost.localdomain localhost4              localhost4.localdomain4\n" \
              "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6\n" \
              "# See hosts(5) for proper format and other examples:\n" \
              "# 192.168.1.10 foo.mydomain.org foo\n" \
              " # 192.168.1.13 bar.mydomain.org bar   "

DST_CONF = '{\n' \
           '"127.0.0.1": "localhost localhost.localdomain localhost4 localhost4.localdomain4",\n' \
           '"::1": "localhost localhost.localdomain localhost6 localhost6.localdomain6"\n' \
           '}'

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
CONF_TYPE = "hosts"
PROJECT_NAME = "_config"


class TestNetworkConfig(BaseTestCase):

    @staticmethod
    def import_network_config_model():
        conf_model = ""
        project_name = CONF_TYPE + PROJECT_NAME
        project_path = BASE_PATH + project_name
        model_name = CONF_TYPE.capitalize() + CONFIG_MODEL_NAME

        try:
            project = importlib.import_module(project_path)
        except ImportError:
            conf_model = ""
        else:
            _conf_model_class = getattr(project, model_name, None)
            if _conf_model_class:
                conf_model = _conf_model_class()
        return conf_model

    def test_parse_res_to_json(self):
        conf_model = self.import_network_config_model()
        conf_json_str = conf_model.parse_res_to_json(CONFIG_TEXT)

        conf_json = json.loads(conf_json_str)
        self.assertEqual(len(conf_json.keys()), 2)

    def test_conf_compare(self):
        conf_model = self.import_network_config_model()
        src_conf = conf_model.parse_res_to_json(CONFIG_TEXT)
        res = conf_model.conf_compare(DST_CONF, src_conf)
        self.assertTrue(res == "SYNCHRONIZED")

    def test_write_conf(self):
        conf_model = self.import_network_config_model()
        conf_dict = conf_model.read_conf(DST_CONF)
        content = conf_model.write_conf(conf_dict)
        conf_content = "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4\n" \
                       "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6\n"
        self.assertTrue(content == conf_content)


if __name__ == '__main__':
    import unittest

    unittest.main()
