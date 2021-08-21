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
import uuid
import unittest
from unittest.mock import MagicMock
from datetime import timedelta
from aops_manager.deploy_manager.ansible_runner.ansible_runner import AnsibleRunner
from aops_manager.deploy_manager.ansible_runner.ansible_runner import ResultCallback
from ansible.executor.task_result import TaskResult
from ansible.inventory.host import Host
from ansible.executor.stats import AggregateStats


def get_mock_task_result(host_name, return_data):
    test_result = TaskResult(
        host=Host(host_name),
        task=get_mock_task(),
        return_data=return_data,
    )

    return test_result


def get_mock_task():
    mock_task = MagicMock()
    mock_task._role = None
    mock_task._parent = None
    mock_task.ignore_errors = False
    mock_task.ignore_unreachable = False
    mock_task._uuid = str(uuid.uuid4())
    mock_task.loop = None
    mock_task.copy.return_value = mock_task
    mock_task.get_name.return_value = "test_task"
    return mock_task


class TestAnsibleRunner(unittest.TestCase):
    def test_get_result(self):
        test_runner = AnsibleRunner(None, None)
        test_callback = ResultCallback()

        test_callback.host_ok["host1"] = {"task_name": "task_host1",
                                          "result": get_mock_task_result("host1",
                                                                         {"host1": "ok"})._result}
        test_callback.host_failed["host2"] = {"task_name": "task_host2",
                                              "result": get_mock_task_result("host2",
                                                                             {"host2": "failed"})._result}
        test_callback.host_skipped["host3"] = {"task_name": "task_host3",
                                               "result": get_mock_task_result("host3",
                                                                              {"host3": "skipped"})._result}
        test_callback.host_unreachable["host4"] = {"task_name": "task_host4",
                                                   "result": get_mock_task_result("host4",
                                                                                  {"host4": "unreachable"})._result}
        test_runner._callback = test_callback
        self.assertDictEqual(test_runner.get_result(),
                             {'success': {'host1': {'task_name': 'task_host1',
                                                    'result': {'host1': 'ok'}}},
                              'failed': {'host2': {'task_name': 'task_host2',
                                                   'result': {'host2': 'failed'}}},
                              'unreachable': {'host4': {'task_name': 'task_host4',
                                                        'result': {'host4': 'unreachable'}}},
                              'skipped': {'host3': {'task_name': 'task_host3',
                                                    'result': {'host3': 'skipped'}}}},
                             msg="get result of all type")

    def test_no_failed(self):
        test_runner = AnsibleRunner("inventory", "password")
        test_runner._results_raw["failed"] = {}
        test_runner._results_raw["unreachable"] = {}
        self.assertTrue(test_runner.no_failed(), msg="No errors have occurred.")

        test_runner._results_raw["failed"] = {"host": "test"}
        test_runner._results_raw["unreachable"] = {}
        self.assertFalse(test_runner.no_failed(), msg="failed errors have occurred.")
        test_runner._results_raw["unreachable"] = {"host": "test"}
        test_runner._results_raw["failed"] = {}
        self.assertFalse(test_runner.no_failed(), msg="unreachable error has occurred.")

        test_runner._results_raw["unreachable"] = {"host": "test1"}
        test_runner._results_raw["failed"] = {"host": "test2"}
        self.assertFalse(test_runner.no_failed(),
                         msg="unreachable and failed error has occurred.")

    def test_run(self):
        test_runner = AnsibleRunner("inventory", "password")
        self.assertIsNone(test_runner.run(None, None, None),
                          msg="Host_list and module is invalid")

    def test_run_playbook(self):
        test_runner = AnsibleRunner("inventory", "password")
        with self.assertRaises(ValueError, msg="Invalid playbook file"):
            test_runner.run_playbook("test")


class TestResultCallback(unittest.TestCase):
    def test_v2_runner_on_ok(self):
        return_data_true = {"changed": "true", "cmd": "source /opt/zookeeper/bin/setId.sh",
                            "delta": "0:00:00.002650",
                            "end": "2021-08-19 11:46:21.142777", "rc": 0,
                            "start": "2021-08-19 11:46:21.140127",
                            "stderr": "", "stderr_lines": [], "stdout": "",
                            "stdout_lines": []}
        test_result = get_mock_task_result("host1", return_data_true)
        result_callback = ResultCallback()
        result_callback.v2_runner_on_ok(test_result)
        self.assertDictEqual(result_callback.host_ok["host1"],
                             {'result': return_data_true,
                              'task_name': 'test_task'})

    def test_v2_runner_on_failed(self):
        return_data = {"changed": "false",
                       "msg": "Failed to download metadata for repo 'Elasticsearch'",
                       "rc": 1, "results": []}
        test_result = get_mock_task_result("host1", return_data)

        result_callback = ResultCallback()
        result_dict = {'result': return_data,
                       'task_name': 'test_task'}

        result_callback.v2_runner_on_failed(test_result)

        self.assertDictEqual(result_callback.host_failed["host1"], result_dict)

    def test_v2_runner_on_unreachable(self):
        return_data = {'ansible_delegated_vars': {'ansible_host': 'host2'}}
        test_result = get_mock_task_result("host1", return_data)
        result_callback = ResultCallback()
        result_dict = {'result': return_data,
                       'task_name': 'test_task'}
        result_callback.v2_runner_on_unreachable(test_result)
        self.assertDictEqual(result_callback.host_unreachable["host1"],
                             result_dict)

    def test_v2_runner_on_skipped(self):
        return_data = {'ansible_delegated_vars': {'ansible_host': 'host2'}}
        test_result = get_mock_task_result("host1", return_data)
        result_callback = ResultCallback()
        result_callback.v2_runner_on_skipped(test_result)
        result_dict = {'result': return_data,
                       'task_name': 'test_task'}

        result_callback.v2_runner_on_skipped(test_result)
        self.assertDictEqual(result_callback.host_skipped["host1"],
                             result_dict)

    def test_v2_playbook_on_stats(self):
        test_stat = AggregateStats()
        result_callback = ResultCallback()
        result_callback.v2_playbook_on_stats(test_stat)

    def test_days_hours_minutes_seconds(self):
        test_time = timedelta(days=64, seconds=29156, microseconds=10)
        self.assertTupleEqual(ResultCallback._days_hours_minutes_seconds(test_time),
                              (64, 8, 5, 28856),
                              msg="day hour minutes second calculate succeed")


if __name__ == "__main__":
    unittest.main()
