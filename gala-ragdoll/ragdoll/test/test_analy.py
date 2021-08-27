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

class TestAnaly():
    """ Test analy """
    def __init__(self, module, d_file):
        self._module = module
        self._file = d_file

    def create_object_by_module(self):
        """
        desc: check the analy object from yang module
        """
        print("############ yang module -> object ############")
        # load all module
        yang_modules = YangModule()
        module_lists = yang_modules.module_list
        print("module_lists is : {}".format(module_lists))
        real_module = []
        for d_module in module_lists:
            if d_module.name() == self._module:
                real_module.append(d_module)
                break
        d_type = yang_modules.getTypeInModdule(real_module)
        conf_type = d_type[self._module]
        object_parse = ObjectParse()
        object_name = object_parse.create_object_by_type(conf_type)
        if object_name.sections():
            print("The object was successfully created.")
        else:
            print("Failed to create object.")
        return real_module[0], conf_type, object_name

    def check_analy_object(self, module, conf_type, d_object):
        result = None
        object_parse = ObjectParse()
        if conf_type == "ini":
            object_parse.add_ini_module_info_in_object(module, d_object)
            contents = Format.get_file_content_by_read(self._file)
            result = object_parse.parse_ini_content_to_object(d_object, contents)

        if result and result.sections():
            print("The yang module is successfully converted to object!")
            print("######### object detail start #########")
            print("the sections is : {}".format(result.sections()))
            for d_section in result.sections():
                print("{}'s items is : {}".format(d_section, result.items(d_section)))
            print("######### object detail end #########")
            content_string = object_parse.parse_object_to_json(result, conf_type)
            print("content_string is : {}".format(content_string))
            if content_string:
                print("Current object is successfully to converted in this project!")
            else:
                print("Current object is failed to converted in this project!")
        else:
            print("The yang module is failed converted to object!")
        return result

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
    test_analy = TestAnaly(config.module, config.file)
    module, conf_type, d_object = test_analy.create_object_by_module()
    rest_object = test_analy.check_analy_object(module, conf_type, d_object)

if __name__ == '__main__':
    main()
