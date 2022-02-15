from __future__ import absolute_import
import requests
import libyang
import os
import sys
import importlib
import argparse
import subprocess
from flask import json
from six import BytesIO

from ragdoll.test import BaseTestCase
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.object_parse import ObjectParse
from ragdoll.controllers.format import Format

class TestConfModel():
    """ Test config_model """
    def __init__(self, module, d_file):
        self._module = module
        self._file = d_file

    def create_config_model_by_yang_module(self): # check: ok
        """
        desc: check the config_model object from yang module
        """
        print("############ test: create_config_model_by_yang_module ############")
        # load all module
        yang_modules = YangModule()
        module_lists = yang_modules.module_list
        #print("{}yang_module_lists: {}.\n".format(" "*4, module_lists))

        real_module = []
        for d_module in module_lists:
            if d_module.name() == self._module:
                real_module.append(d_module)
                break

        d_type = yang_modules.getTypeInModdule(real_module)
        conf_type = d_type[self._module]

        object_parse = ObjectParse()
        conf_model = object_parse.create_conf_model_by_type(conf_type)
        if conf_model:
            print("{}yang: {}, conf_type: {}, conf_model: {}\n".format(" "*4, real_module[0], conf_type, conf_model))
            print("The config_model was successfully created.\n")
        else:
            print("Failed to create config_model.\n")
        return real_module[0], conf_type, conf_model

    def check_config_model(self, yang_module, conf_type, conf_model):
        """
        desc: Check the serialization function of the conf_model
        """
        print("############ test: check_config_model ############")
        result = None
        conf_info = Format.get_file_content_by_read(self._file)
        print("{}conf_info: {}".format(" "*4, conf_info))

        conf_model.load_yang_model(yang_module)
        conf_model.read_conf(conf_info)
        print("{}conf_info in model: {}.\n".format(" "*4, conf_model.conf))

        object_parse = ObjectParse()
        conf_json = object_parse.parse_model_to_json(conf_model)
        if conf_json:
            print("{}conf_json: {}\n".format(" "*4, conf_json))
            print("Current config_model is successfully to converted in this project!\n")
        else:
            print("Current config_model is failed to converted in this project!\n")
        return conf_model

def parse_command_line():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(prog="test_config_model")
    parser.add_argument("-m", "--module", nargs="?", required=True,
                        help="The object which you want to analy")
    parser.add_argument("-f", "--file", nargs="?", required=True,
                        help="The file used as input for parsing")

    config = parser.parse_args()

    if config.module is None:
        parser.print_help()
        sys.exit(0)
    else:
        return config

def main():
    """Entry point for test_config_model"""
    config = parse_command_line()
    test_config_model = TestConfModel(config.module, config.file)
    module, conf_type, conf_model = test_config_model.create_config_model_by_yang_module()
    rest_object = test_config_model.check_config_model(module, conf_type, conf_model)

if __name__ == '__main__':
    main()
