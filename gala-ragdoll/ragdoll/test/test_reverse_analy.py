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
from ragdoll.test.test_analy import TestAnaly

class TestReverseAnaly():
    """ Test reverse analy """
    def __init__(self, module, d_file):
        self._module = module
        self._file = d_file

    def create_object_with_content(self):
        """
        desc: create the object with the content of the input file.
        """
        test_analy = TestAnaly(self._module, self._file)
        module, conf_type, d_object = test_analy.create_object_by_module()
        rest_object = test_analy.check_analy_object(module, conf_type, d_object)
        return rest_object

    def check_reverse_analy_object(self, d_object):
        """
        desc: check the inverse analy from object
        """
        print("############ object -> content ############")
        object_parse = ObjectParse()
        content = object_parse.parse_object_to_ini_content(d_object)
        if content:
            print("The object is successfully converted to content!")
            print("The content is : {}".format(content))
        else:
            print("The object is failed converted to content, please check the analy script!")
        return content

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
    d_object = test_reverse_analy.create_object_with_content()
    content = test_reverse_analy.check_reverse_analy_object(d_object)

if __name__ == '__main__':
    main()
