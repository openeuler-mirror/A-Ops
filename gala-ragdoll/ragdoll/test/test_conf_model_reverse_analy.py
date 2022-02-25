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
from ragdoll.test.test_conf_model import TestConfModel

class TestReverseAnaly():
    """ Test reverse analy """
    def __init__(self, module, d_file):
        self._module = module
        self._file = d_file

    def create_conf_model_with_conf_info(self):
        """
        desc: create the object with the conf_info of the input file.
        """
        print("############ test: create_conf_model_with_conf_info ############")
        test_analy = TestConfModel(self._module, self._file)
        yang_module, conf_type, _conf_model = test_analy.create_config_model_by_yang_module()
        conf_model = test_analy.check_config_model(yang_module, conf_type, _conf_model)
        return conf_model

    def check_reverse_conf_model(self, d_object):
        """
        desc: check the deserialization from conf_model
        """
        print("############ test: check_reverse_conf_model ############")
        conf_info = d_object.write_conf()
        if conf_info:
            print("The conf_info is : {}".format(conf_info))
            print("The object is successfully converted to conf_info!")
        else:
            print("The object is failed converted to conf_info, please check the analy script!")
        return conf_info

def parse_command_line():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(prog="test_analy")
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
    """Entry point for test_analy"""
    config = parse_command_line()
    test_reverse_analy = TestReverseAnaly(config.module, config.file)
    d_object = test_reverse_analy.create_conf_model_with_conf_info()
    content = test_reverse_analy.check_reverse_conf_model(d_object)

if __name__ == '__main__':
    main()
