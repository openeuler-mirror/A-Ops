# Author: Lay
# Description: default
# Date: 2023/6/16 17:42
import importlib
import json

config_text = "   # Loopback entries; do not change.\n" \
              " # For historical reasons, localhost precedes localhost.localdomain:\n" \
              "127.0.0.1   localhost         localhost.localdomain localhost4              localhost4.localdomain4\n" \
              "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6\n" \
              "# See hosts(5) for proper format and other examples:\n" \
              "# 192.168.1.10 foo.mydomain.org foo\n" \
              " # 192.168.1.13 bar.mydomain.org bar   "

dst_conf = '{\n' \
           '"127.0.0.1": "localhost localhost.localdomain localhost4 localhost4.localdomain4",\n' \
           '"::1": "localhost localhost.localdomain localhost6 localhost6.localdomain6"\n' \
           '}'

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
conf_type = "network"
PROJECT_NAME = "_config"

from ragdoll.test import BaseTestCase


class TestNetworkConfig(BaseTestCase):

    def import_network_config_model(self):
        conf_model = ""
        project_name = conf_type + PROJECT_NAME
        project_path = BASE_PATH + project_name
        model_name = conf_type.capitalize() + CONFIG_MODEL_NAME

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
        conf_json_str = conf_model.parse_res_to_json(config_text)
        print("conf_json_str : {}".format(conf_json_str))

        conf_json = json.loads(conf_json_str)
        self.assertEqual(len(conf_json.keys()), 2)

    def test_conf_compare(self):
        conf_model = self.import_network_config_model()
        src_conf = conf_model.parse_res_to_json(config_text)
        res = conf_model.conf_compare(dst_conf, src_conf)
        print("res : {}".format(res))
        self.assertTrue(res == "SYNCHRONIZED")

    def test_write_conf(self):
        conf_model = self.import_network_config_model()
        conf_dict = conf_model.read_conf(dst_conf)
        print("read_conf : {}".format(conf_dict))
        content = conf_model.write_conf(conf_dict)
        print("content : {}".format(content))
        conf_content = "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4\n" \
                       "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6\n"
        self.assertTrue(content == conf_content)


if __name__ == '__main__':
    import unittest

    unittest.main()
