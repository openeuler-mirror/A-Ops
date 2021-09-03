#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Author: YangYunYi
Date: 2021/8/4 15:56
docs: check_rule_manager.py
description: Check Ruler manager
"""
import yaml
from adoctor_check_executor.common.config import CHECK_RULE_PLUGIN_CONFIG_PATH, \
    executor_check_config
from adoctor_check_executor.common.check_error import CheckExceptionList, CheckPluginError
from aops_utils.log.log import LOGGER
from aops_utils.singleton import singleton


@singleton
class CheckRuleManager:
    """
    The manager of Check rule

    Attributes:
        plugins: dict to record plugin
    """

    def __init__(self):
        """
        Constructor
        """
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        """
        Load plugin

        Returns:
            None

        Raise:
            CheckPluginError

        """
        with open(CHECK_RULE_PLUGIN_CONFIG_PATH, 'r') as plugin_config:
            plugin_list = yaml.safe_load(plugin_config)
            if "plugin_list" not in plugin_list:
                LOGGER.error("Plugin list has no plugin_list")
                raise CheckPluginError("Config file cannot find plugin_list")
            for plugin_info in plugin_list["plugin_list"]:
                plugin_name = plugin_info.get("plugin_name")
                file_name = plugin_info.get("file_name")
                module_name = plugin_info.get("module_name")
                if not all([plugin_name, file_name, module_name]):
                    LOGGER.error("Invalid plugin_name or file_name or module_name")
                    raise CheckPluginError("Config file cannot find plugin_list")
                self.run_plugin(plugin_name, module_name, file_name)

    def run_plugin(self, plugin_name, module_name, file_name):
        """
        Load the plugin and generate the object.

        Returns:
            None

        Raise:
            CheckPluginError

        """
        try:
            plugin_module = __import__(executor_check_config.executor.get("PLUGIN_PATH")
                                       + '.' + file_name,
                                       fromlist=[module_name])
            plugin_class = getattr(plugin_module, module_name)
            self.plugins[plugin_name] = plugin_class
        except CheckExceptionList as exp:
            raise CheckPluginError("Load check plugin failed") from exp

    def unload_plugin(self, plugin_name):
        """
        Unload the plugin from check rule manager.

        Returns:
            plugin_name (str): plugin name

        Raise:
            CheckPluginError
        """
        if plugin_name not in self.plugins.keys():
            LOGGER.error("Invalid plugin name %s", plugin_name)
            raise CheckPluginError("Cannot find plugin %s to unload" % plugin_name)
        self.plugins.pop(plugin_name)

    def get_plugin(self, plugin_name):
        """
        Get the plugin object.

        Returns:
            plugin_name (str): plugin name

        """
        LOGGER.debug("plugin_name %s, self.plugins %s", plugin_name, self.plugins)
        plugin_class = self.plugins.get(plugin_name)
        if not plugin_class:
            raise CheckPluginError("Cannot find plugin %s to load" % plugin_name)
        plugin_obj = plugin_class()
        plugin_obj.set_plugin_manager(self)
        return plugin_obj


check_rule_manager = CheckRuleManager()
