from __future__ import absolute_import
import requests
import libyang
import os
import sys
import importlib
from flask import json
from six import BytesIO

from ragdoll.test import BaseTestCase
from ragdoll.utils.yang_module import YangModule

class TestYang(BaseTestCase):

    def test_yang_module(self):
        yang_module = YangModule()
        yangdir = yang_module.yang_dir
        print("yangdir is : {}".format(yangdir))
        if not yangdir:
            return False

        failed_module = []
        success_module = []
        for root, dirs, files in os.walk(yangdir):
            for d_file in files:
                module_path = os.path.join(yangdir, d_file)
                grammar_res = yang_module.check_yang_grammar(module_path)
                if grammar_res:
                    success_module.append(module_path)
                else:
                    failed_module.append(module_path)
        print("\n")
        print("The result of test_yang_module is : {}".format(success_module))
        self.assertEqual(len(failed_module), 0)

    def test_yang_extension(self):
        res = {}
        success_module = []
        failed_module = []
        yang_module = YangModule()
        module_list = yang_module.module_list
        path_list = yang_module.getFilePathInModdule(module_list)
        d_type_list = yang_module.getTypeInModdule(module_list)
        spacer_list = yang_module.getSpacerInModdule(module_list)
        for d_module in module_list:
            module_name = d_module.name()
            ext = {}
            ext['path'] = path_list[module_name]
            ext['type'] = d_type_list[module_name]
            ext['spacer'] = spacer_list[module_name]
            res[module_name] = ext
            if ext['path'] and ext['type'] and ext['spacer']:
                success_module.append(module_name)
            else:
                failed_module.append(module_name)
        print("\n")
        print("The result of test_yang_extension is : {}".format(res))
        self.assertEqual(len(failed_module), 0)

    def test_yang_xpath(self):
        xpath_list = []
        failed_module = []
        yang_module = YangModule()
        module_list = yang_module.module_list
        for d_module in module_list:
            xpath = yang_module.getXpathInModule(d_module)
            if xpath:
                xpath_list.append(xpath)
            else:
                failed_module.append(xpath)

        print("\n")
        print("The result of test_yang_xpath is : {}".format(xpath_list))
        self.assertEqual(len(failed_module), 0)

if __name__ == '__main__':
    import unittest
    unittest.main()
