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
import grp
import os
import pwd
import unittest
from unittest import mock

from libconf import AttrDict
from aops_agent.tools.util import get_file_info, change_probe_status

target_probes = (AttrDict([('name', 'test_no_check_1'),
                           ('command', 'test'),
                           ('param', ''),
                           ('switch', 'on')]),
                 AttrDict([('name', 'test_no_check_2'),
                           ('command', ''),
                           ('param', ''),
                           ('switch', 'off')]),
                 AttrDict([('name', 'test_with_check_1'),
                           ('command', ''),
                           ('param', ''),
                           ('start_check', ''),
                           ('check_type', 'count'),
                           ('switch', 'on')]),
                 AttrDict([('name', 'test_with_check_2'),
                           ('command', ''),
                           ('param', ''),
                           ('start_check', ''),
                           ('check_type', 'count'),
                           ('switch', 'off')]),
                 AttrDict([('name', 'test_with_check_3'),
                           ('command', ''),
                           ('param', ''),
                           ('start_check', ''),
                           ('check_type', 'count'),
                           ('switch', 'auto')]),
                 AttrDict([('name', 'test_with_check_4'),
                           ('command', ''),
                           ('param', ''),
                           ('start_check', ''),
                           ('check_type', 'count'),
                           ('switch', 'auto')]),
                 )


class TestGetFileInfo(unittest.TestCase):

    @mock.patch.object(pwd, 'getpwuid')
    @mock.patch.object(grp, 'getgrgid')
    @mock.patch('aops_agent.tools.util.os.stat')
    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_file_content_when_target_file_exist_and_not_executable_and_less_than_1M(
            self, mock_os_access, mock_getsize, mock_os_stat, mock_getgrgid, mock_getpwduid):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_os_stat.st_mode.return_value = 33198
        mock_os_stat.st_uid.return_value = '123456'
        mock_os_stat.st_gid.return_value = '123456'
        mock_getsize.return_value = 1024
        mock_getgrgid.return_value = 1001,
        mock_getpwduid.return_value = 1001,
        with mock.patch('builtins.open', mock.mock_open(read_data='123456')):
            info = get_file_info(file_path)
        self.assertEqual('123456', info.get('content'))

    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_can_execute(
            self, mock_os_access):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = True
        info = get_file_info(file_path)
        self.assertEqual({}, info)

    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_is_larger_than_1M(
            self, mock_os_access, mock_getsize):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_getsize.return_value = 1024 * 1024 * 2
        info = get_file_info(file_path)
        self.assertEqual({}, info)

    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_is_not_encoded_by_utf8(
            self, mock_os_access, mock_getsize):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_getsize.return_value = 1024 * 1024
        with mock.patch('builtins.open', mock.mock_open()) as mock_file:
            mock_file.side_effect = UnicodeDecodeError('', bytes(), 1, 1, '')
            info = get_file_info(file_path)
        self.assertEqual({}, info)


class TestChangeProbeStatus(unittest.TestCase):
    def test_change_probe_status_should_return_success_list_and_empty_failure_list_when_input_all_right(
            self):
        probe_status = {
            'test_no_check_1': 'off',
            "test_no_check_2": "on",
            "test_with_check_1": "auto",
            "test_with_check_2": "auto",
            "test_with_check_3": "on",
            "test_with_check_4": "off"
        }
        res, fail_list = change_probe_status(target_probes, probe_status, {'success': []})
        expect_success_res = list(probe_status.keys())
        self.assertEqual((expect_success_res, {}), (res['success'], fail_list))

    def test_change_probe_status_should_return_success_list_and_failure_list_when_part_of_input_probe_name_is_not_in_target_probes(
            self):
        probe_status = {
            'test_no_check_1': 'off',
            "test_no_check_3": "on",
            "test_with_check_1": "auto",
            "test_with_check_2": "auto",
            "test_with_check_3": "on",
            "test_with_check_5": "off"
        }
        res, fail_list = change_probe_status(target_probes, probe_status, {'success': []})
        expect_success_res = ['test_no_check_1', 'test_with_check_1', 'test_with_check_2',
                              'test_with_check_3']
        expect_fail_res = {"test_no_check_3": "on", "test_with_check_5": "off"}
        self.assertEqual((expect_success_res, expect_fail_res), (res['success'], fail_list))

    def test_change_probe_status_should_return_failure_list_when_input_probe_name_is_not_support_auto(
            self):
        probe_status = {
            'test_no_check_1': 'auto',
            "test_no_check_2": "auto"
        }
        res, fail_list = change_probe_status(target_probes, probe_status, {'success': []})
        expect_fail_res = {"test_no_check_1": "auto", "test_no_check_2": "auto"}
        self.assertEqual(expect_fail_res, fail_list)
