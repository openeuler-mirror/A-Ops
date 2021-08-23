# !/usr/bin/python3
# coding: utf-8
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/

import os
import shutil
import unittest
from unittest.mock import patch
from aops_manager.deploy_manager.run_task import TaskRunner
from aops_manager.deploy_manager.config import TASKS_PATH

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestTaskRunner(unittest.TestCase):
    @patch("aops_manager.deploy_manager.run_task.AnsibleRunner")
    def test_run_playbook(self, ansible_runner_mock):
        inventory_name = "test_inventory"
        vault_pwd = "vault_pwd"
        self.assertTupleEqual(TaskRunner.run_playbook(None, None, None),
                              (False, None),
                              msg="Invalid parameter")
        self.assertTupleEqual(TaskRunner.run_playbook(inventory_name, "", vault_pwd),
                              (False, None),
                              msg="Invalid inventory path")
        result_dict = {"success": {"host1": "ok"},
                       "failed": {"host2": "failed"},
                       "skipped": {"host3": "skipped"},
                       "unreachable": {"host4": "unreachable"}}
        instance = ansible_runner_mock.return_value
        instance.run_playbook.return_value = None
        instance.get_result.return_value = result_dict
        instance.no_failed.return_value = False

        self.assertTupleEqual(TaskRunner.run_playbook("mysql", "mysql", vault_pwd),
                              (False, result_dict))

    @patch.object(TaskRunner, "run_playbook")
    def test_run_task(self, run_playbook_mock):
        self.assertFalse(TaskRunner.run_task(None, None),
                         msg="Invalid task name")
        self.assertFalse(TaskRunner.run_task("", ""),
                         msg="Invalid ")

        result_dict = {"success": {"host1": "ok"},
                       "failed": {"host2": "failed"},
                       "skipped": {"host3": "skipped"},
                       "unreachable": {"host4": "unreachable"}}
        run_playbook_mock.side_effect = [(True, result_dict), (False, result_dict)]

        shutil.copy("test_task.yml", os.path.join(TASKS_PATH, "test_task.yml"))
        self.assertTrue(TaskRunner.run_task("test_task", "11765421"),
                        msg="Run task succeed")
        self.assertFalse(TaskRunner.run_task("test_task", "11765421"),
                         msg="Run task failed")
        os.remove(os.path.join(TASKS_PATH, "test_task.yml"))


if __name__ == "__main__":
    unittest.main()
