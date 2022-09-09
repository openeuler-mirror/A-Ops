#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import subprocess
import unittest
from unittest import mock

from aops_agent.conf.status import SUCCESS, FILE_NOT_FOUND
from aops_agent.manages.plugin_manage import Plugin
from aops_agent.models.custom_exception import InputError


class TestPluginManage(unittest.TestCase):
    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_start_service_should_return_success_when_plugin_is_already_running(
            self, mock_shell_data, mock_popen):
        mock_return_value = "test-res-running"
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, mock_return_value]
        res = Plugin('test').start_service()
        self.assertEqual(SUCCESS, res)

    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_start_service_should_return_success_when_make_plugin_running_successful(
            self, mock_shell_data, mock_popen):
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, '', 'active']
        res = Plugin('test').start_service()
        self.assertEqual(SUCCESS, res)

    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_start_service_should_return_file_not_found_when_plugin_is_not_installed(
            self, mock_shell_data, mock_popen):
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, '', 'service not found']
        res = Plugin('test').start_service()
        self.assertEqual(FILE_NOT_FOUND, res)

    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_start_service_should_return_file_not_found_when_host_has_no_command(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Plugin('test').start_service()
        self.assertEqual(FILE_NOT_FOUND, res)

    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_stop_service_should_return_success_when_plugin_is_already_stopping(
            self, mock_shell_data, mock_popen):
        mock_return_value = "test-res-inactive"
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, mock_return_value]
        res = Plugin('test').stop_service()
        self.assertEqual(SUCCESS, res)

    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_stop_service_should_return_success_when_make_plugin_running_successful(
            self, mock_shell_data, mock_popen):
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, '', 'inactive']
        res = Plugin('test').stop_service()
        self.assertEqual(SUCCESS, res)

    @mock.patch.object(subprocess, 'Popen')
    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_stop_service_should_return_file_not_found_when_plugin_is_not_installed(
            self, mock_shell_data, mock_popen):
        mock_popen.stdout.return_value = None
        mock_shell_data.side_effect = [subprocess.Popen, '', 'service not found']
        res = Plugin('test').stop_service()
        self.assertEqual(FILE_NOT_FOUND, res)

    @mock.patch('aops_agent.manages.plugin_manage.get_shell_data')
    def test_stop_service_should_return_file_not_found_when_host_has_no_command(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Plugin('test').stop_service()
        self.assertEqual(FILE_NOT_FOUND, res)