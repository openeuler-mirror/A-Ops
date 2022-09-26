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
import unittest
import warnings
from unittest import mock

import responses

from aops_agent.conf.status import SUCCESS, PARAM_ERROR
from aops_agent.manages.command_manage import Command
from aops_agent.models.custom_exception import InputError


class TestCommandManage(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter('ignore', ResourceWarning)

    @responses.activate
    def test_register_should_return_200_when_input_correct(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "agent_port": "12000"
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": SUCCESS},
                      status=SUCCESS,
                      content_type='application/json'
                      )
        data = Command.register(input_data)
        self.assertEqual(SUCCESS, data)

    def test_register_should_return_param_error_when_input_web_username_is_null(self):
        input_data = {
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_username_is_not_string(self):
        input_data = {
            "web_username": 12345,
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_password_is_null(self):
        input_data = {
            "web_username": "admin",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_password_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": 123456,
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": 12345,
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": True,
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_not_boolean(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": "string",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_ip_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_ip_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_port_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": 80
        }
        data = Command.register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_agent_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "agent_port": 11000
        }
        data = Command.register(input_data)
        self.assertEqual(data, PARAM_ERROR)

    @responses.activate
    def test_register_should_return_success_when_input_with_no_agent_port(self):
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": SUCCESS},
                      status=SUCCESS,
                      content_type='application/json'
                      )
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
        }
        data = Command.register(input_data)
        self.assertEqual(SUCCESS, data)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_info_should_return_memory_info_when_get_shell_data_is_correct(
            self, mock_shell_data):
        mock_shell_data.return_value = """
            Memory Device
                    Array Handle: 0x0006
                    Error Information Handle: Not Provided
                    Total Width: 72 bits
                    Data Width: 64 bits
                    Size: 16 GB
                    Form Factor: DIMM
                    Set: None
                    Locator: DIMM170 J31
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 0
                    Type: DDR4
                    Type Detail: Synchronous Registered (Buffered)
                    Speed: 2000 MT/s
                    Manufacturer: Test1
                    Serial Number: 129C7699
                    Asset Tag: 1939
                    Part Number: HMA82GR7CJR4N-WM
            Memory Device
                    Form Factor: DIMM
                    Set: None
                    Size: 32 GB
                    Locator: DIMM170 J31
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 0
                    Type: DDR4
                    Type Detail: Synchronous Registered (Buffered)
                    Speed: 2000 MT/s
                    Manufacturer: Test2
            """
        expect_res = {
            'total': 2,
            'info': [
                {'size': '16 GB',
                 'type': 'DDR4',
                 'speed': '2000 MT/s',
                 'manufacturer': 'Test1'
                 },
                {'size': '32 GB',
                 'type': 'DDR4',
                 'speed': '2000 MT/s',
                 'manufacturer': 'Test2'
                 }
            ]
        }

        res = Command()._get_memory_info()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_info_should_return_empty_list_when_memory_info_is_not_showed(
            self, mock_shell_data):
        mock_shell_data.return_value = """
                    Memory Device
                    Array Handle: 0x0006
                    Error Information Handle: Not Provided
                    Total Width: Unknown
                    Data Width: Unknown
                    Size: No Module Installed
                    Form Factor: DIMMis
                    Set: None
                    Locator: DIMM171 J32
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 1
                    Type: Unknown
                    Type Detail: Unknown Synchronous
                    Speed: Unknown
        """
        expect_res = {'info': [], 'total': 0}

        res = Command()._get_memory_info()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_info_should_return_empty_dict_when_get_shell_data_is_incorrect_data(
            self, mock_shell_data):
        """
            This situation exists in the virtual machine
        """
        mock_shell_data.return_value = """
                test text 
        """
        res = Command()._get_memory_info()
        self.assertEqual({}, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_info_should_return_empty_dict_when_get_shell_data_error(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command()._get_memory_info()
        self.assertEqual({}, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_size_should_return_memory_size_when_get_shell_data_is_correct_data(
            self, mock_shell_data):
        mock_shell_data.return_value = '''
            Memory block size:       128M
            Total online memory:     2.5G
            Total offline memory:      0B
        '''
        res = Command._Command__get_total_online_memory()
        self.assertEqual('2.5G', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_size_should_return_empty_str_when_get_shell_data_is_incorrect_data(
            self, mock_shell_data):
        mock_shell_data.return_value = '''
            Memory block size:       128M
        '''
        res = Command._Command__get_total_online_memory()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_memory_size_should_return_empty_str_when_get_shell_data_error(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command._Command__get_total_online_memory()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_cpu_info_should_return_correct_info_when_execute_command_successful(
            self, mock_shell_data):
        mock_shell_data.return_value = 'Architecture:                    x86_64\n' \
                                       'CPU(s):                          1\n' \
                                       'Model name:                      AMD Test\n' \
                                       'Vendor ID:                       AuthenticAMD\n' \
                                       'L1d cache:                       32 KiB\n' \
                                       'L1i cache:                       32 KiB\n' \
                                       'L2 cache:                        512 KiB\n' \
                                       'L3 cache:                        8 MiB\n'
        expect_res = {
            "architecture": "x86_64",
            "core_count": "1",
            "model_name": "AMD Test",
            "vendor_id": "AuthenticAMD",
            "l1d_cache": "32 KiB",
            "l1i_cache": "32 KiB",
            "l2_cache": "512 KiB",
            "l3_cache": "8 MiB"
        }
        res = Command._get_cpu_info()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_cpu_info_should_return_null_when_execute_command_successful_but_not_get_expected_information(
            self, mock_shell_data):
        mock_shell_data.return_value = ''
        expect_res = {
            "architecture": None,
            "core_count": None,
            "model_name": None,
            "vendor_id": None,
            "l1d_cache": None,
            "l1i_cache": None,
            "l2_cache": None,
            "l3_cache": None
        }
        res = Command._get_cpu_info()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_cpu_info_should_return_empty_dict_when_host_has_no_command_lscpu(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command._get_cpu_info()
        self.assertEqual({}, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_kernel_version_should_return_cpu_info_when_execute_command_successfully(
            self, mock_shell_data):
        mock_shell_data.return_value = '5.10.0-5.10.0.24.oe1.x86_64'
        expect_res = '5.10.0-5.10.0.24'
        res = Command._Command__get_kernel_version()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_kernel_version_should_return_empty_string_when_execute_command_successfully_but_not_get_expected_information(
            self, mock_shell_data):
        mock_shell_data.return_value = 'test_info'
        res = Command._Command__get_kernel_version()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_kernel_version_should_return_cpu_info_when_host_has_no_command_uname(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command._Command__get_kernel_version()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_bios_version_should_return_cpu_info_when_execute_command_successfully(
            self, mock_shell_data):
        mock_shell_data.return_value = """
                BIOS Information
                Vendor: innotek GmbH
                Version: VirtualBox
                Release Date: 12/01/2006
                Address: 0xE0000
                Runtime Size: 128 kB
                ROM Size: 128 kB
                Characteristics:
                        ISA is supported
                        PCI is supported
                        Boot from CD is supported
                        Selectable boot is supported
                        8042 keyboard services are supported (int 9h)
                        CGA/mono video services are supported (int 10h)
                        ACPI is supported
        """
        expect_res = 'VirtualBox'
        res = Command._Command__get_bios_version()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_bios_version_should_return_empty_string_when_execute_command_successfully_but_not_get_expected_information(
            self, mock_shell_data):
        mock_shell_data.return_value = 'test_info'
        res = Command._Command__get_bios_version()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_bios_version_should_return_cpu_info_when_host_has_no_command_dmidecode(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command._Command__get_bios_version()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_system_info_should_return_cpu_info_when_execute_command_successfully(
            self, mock_shell_data):
        mock_shell_data.return_value = """
                    NAME="openEuler"
                    VERSION="21.09"
                    ID="openEuler"
                    VERSION_ID="21.09"
                    PRETTY_NAME="openEuler 21.09"
                    ANSI_COLOR="0;31"
        """
        expect_res = 'openEuler 21.09'
        res = Command._Command__get_system_info()
        self.assertEqual(expect_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_system_info_should_return_empty_string_when_execute_command_successfully_but_not_get_expected_information(
            self, mock_shell_data):
        mock_shell_data.return_value = 'test_info'
        res = Command._Command__get_system_info()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_system_info_should_return_cpu_info_when_host_has_no_command_cat(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command._Command__get_system_info()
        self.assertEqual('', res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_disk_info_should_return_disk_info_when_all_software_is_running_fine(
            self, mock_shell_data):
        mock_shell_data.return_value = """
            {
                "product": "test-model", 
                "size": 20000000000
            }
        """
        expected_res = [{'model': 'test-model', 'capacity': 20}]
        res = Command()._get_disk_info()
        self.assertEqual(expected_res, res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_disk_info_should_return_empty_list_when_command_excute_is_failed(
            self, mock_shell_data):
        mock_shell_data.side_effect = InputError('')
        res = Command()._get_disk_info()
        self.assertEqual([], res)

    @mock.patch('aops_agent.manages.command_manage.get_shell_data')
    def test_get_disk_info_should_return_empty_list_when_when_command_excute_is_succeed_but_cannot_get_correct_info(
            self, mock_shell_data):
        mock_shell_data.return_value = ""
        res = Command()._get_disk_info()
        self.assertEqual([], res)
