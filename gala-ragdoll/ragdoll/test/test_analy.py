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

class TestAnaly():
    """ Test analy """
    def __init__(self, module, file):
        self._module = module
        self._file = file

    def check_analy_object(self):
        # 加载所有的yang modules:
        yang_modules = YangModule()
        d_type = yang_modules.getTypeInModdule(self._module)

        # module_list = yang_modules.module_list
        print("modulesList is : {}".format(module_list))
        module = yang_modules.getModuleByFilePath(self.file)

        d_object = yang_modules.create_ini_object(module)
        yang_modules.add_module_info_in_object(module, d_object)
        print("d_object is : {}".format(d_object))

def parse_command_line():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(prog="test_analy")
    parser.add_argument("-m", "--module", nargs="?",
                        help="The object which you want to analy")
    parser.add_argument("-f", "--file", nargs="?",
                        help="The file used as input for parsing")

    config = parser.parse_args()

    if config.object is None:
        parser.print_help()
        sys.exit(0)
    else:
        return config

def main():
    """Entry point for test_analy"""
    config = parse_command_line()
    test_analy = TestAnaly(config.module, config.d_file)
    test_analy.check_analy_object()

if __name__ == '__main__':
    main()