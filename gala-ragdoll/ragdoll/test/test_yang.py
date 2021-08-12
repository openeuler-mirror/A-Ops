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

    yang_module = YangModule()

    def test_yang_module(self):
        self.module_list = yang_module.loadYangModules()
        if self.module_list >= 1:
            self.assert200(module_list,
                       'module_list is : ' + module_list)
        else:
            self.assert500(module_list,
                       'module_list is : ' + module_list)

    def test_yang_xpath(self):
        xpath_list = []
        for d_module in self.module_list:
            xpath = yang_module.getXpathInModule(d_module)
            xpath_list.append(xpath)

        if len(xpaxpath_listth) == len(self.module_list):
            self.assert200(xpath_list,
                       'xpath_list is : ' + xpath_list)
        else:
            self.assert500(xpath_list,
                       'xpath_list is : ' + xpath_list)

    def test_yang_extension_path(self):
        ext_path = []
        for d_module in self.module_list:
            path = yang_module.getFilePathInModdule(d_module)
            ext_path.append(path)

        if len(ext_path) == len(self.module_list):
            self.assert200(ext_path,
                       'ext_path is : ' + ext_path)
        else:
            self.assert500(ext_path,
                       'ext_path is : ' + ext_path)

    def test_yang_extension_type(self):
        ext_type = []
        for d_module in self.module_list:
            d_type = yang_module.getTypeInModdule(d_module)
            ext_type.append(d_type)

        if len(ext_type) == len(self.module_list):
            self.assert200(ext_type,
                       'ext_type is : ' + ext_type)
        else:
            self.assert500(ext_types,
                       'ext_type is : ' + ext_type)

    def test_yang_extension_spacer(self):
        ext_spacer = []
        for d_module in self.module_list:
            spacer = yang_module.getSpacerInModdule(d_module)
            ext_type.append(spacer)

        if len(ext_spacer) == len(self.module_list):
            self.assert200(ext_spacer,
                       'ext_spacer is : ' + ext_spacer)
        else:
            self.assert500(ext_type,
                       'ext_spacer is : ' + ext_spacer)

if __name__ == '__main__':
    import unittest
    unittest.main()
