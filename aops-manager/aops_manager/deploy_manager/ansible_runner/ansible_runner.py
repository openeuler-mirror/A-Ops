# coding: utf-8
# !/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: Ansible running entry
Class: AnsibleRunner
"""
import os
from datetime import datetime
from ansible import context
from ansible import constants as Constants
from ansible.errors import AnsibleError
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.module_utils.common.collections import ImmutableDict
from ansible.utils.color import colorize, hostcolor
from aops_manager.deploy_manager.ansible_runner.vault_handler import VaultHandler
from aops_utils.log.log import LOGGER


class AnsibleRunner:
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, inventory_source, vault_password):
        """
        Construct Function
        Args:
            inventory_source (str): the inventory dirs, files, script paths or lists of hosts
            vault_password (str): The password to decrypt host vars
        """
        # the inventory dirs, files, script paths or lists of hosts
        self._inventory_source = inventory_source

        # vault to decrypt host vars
        self._vault_password = vault_password
        # data loader
        self._loader = DataLoader()
        # InventoryManager
        self._inventory_manager = None
        # variable_manager
        self._variable_manager = None

        # Task execution result callback
        self._callback = ResultCallback()
        # run result
        self._results_raw = dict()
        # Initializing Data
        self._initialize_data()

    def _initialize_data(self):
        """
        Initializing the Ansible Configuration
        """
        context.CLIARGS = ImmutableDict(
            connection='smart',
            remote_user='aops',
            private_key_file=None,
            module_path=None,
            become=None,
            become_method='su',
            become_user='root',
            verbosity=3,
            listhosts=None,
            listtasks=None,
            listtags=None,
            syntax=None,
            start_at_task=None,
        )

        # Get vault password
        vault_secrets = VaultHandler.setup_vault_secrets(self._loader,
                                                         vault_password=self._vault_password,
                                                         )
        self._loader.set_vault_secrets(vault_secrets)
        self._inventory_manager = InventoryManager(
            loader=self._loader, sources=self._inventory_source)
        self._variable_manager = VariableManager(
            loader=self._loader, inventory=self._inventory_manager)

    def run(self, host_list, module_name, module_args):
        """
        Run module from ansible ad-hoc.
        Args:
            host_list (list): Host List
            module_name (str): module name
            module_args (list): module parameters

        Raise:
            AnsibleError
        """
        if not module_name:
            LOGGER.error("Invalid module_name")
            return None
        play_source = dict(
            name="Ansible Ad-hoc Command",
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )
        play = Play().load(play_source,
                           variable_manager=self._variable_manager,
                           loader=self._loader)

        task_queue_manager = None
        try:
            task_queue_manager = TaskQueueManager(
                inventory=self._inventory_manager,
                variable_manager=self._variable_manager,
                loader=self._loader,
                stdout_callback='default',
                passwords=None
            )
            task_queue_manager._stdout_callback = self._callback
            result = task_queue_manager.run(play)
            LOGGER.debug("Run result %s", result)
            return result
        except AnsibleError as exp:
            LOGGER.exception(exp)
            raise
        finally:
            if task_queue_manager is not None:
                task_queue_manager.cleanup()

    def run_playbook(self, playbook_file):
        """
        Run play book.
        Args:
            playbook_file (str): playbook file path

        Returns:
            None

        Raise:
            ValueError
            AnsibleError
        """

        # since the API is constructed for CLI it expects certain
        # options to always be set in the context object
        try:
            if not os.path.exists(playbook_file):
                raise ValueError("Invalid playbook file ", playbook_file)
            executor = PlaybookExecutor(
                playbooks=[playbook_file],
                inventory=self._inventory_manager,
                variable_manager=self._variable_manager,
                loader=self._loader,
                passwords=None
            )
            executor._tqm._stdout_callback = self._callback
            executor.run()
        except AnsibleError as exp:
            LOGGER.exception(exp)
            raise

    def get_result(self):
        """
        Obtaining the Running Output Information

        Returns:
            result information
        """

        self._results_raw = {'success': {}, 'failed': {}, 'unreachable': {}, 'skipped': {}}
        for host, result in self._callback.host_ok.items():
            self._results_raw['success'][host] = result

        for host, result in self._callback.host_failed.items():
            self._results_raw['failed'][host] = result

        for host, result in self._callback.host_skipped.items():
            self._results_raw['skipped'][host] = result

        for host, result in self._callback.host_unreachable.items():
            self._results_raw['unreachable'][host] = result

        return self._results_raw

    def no_failed(self):
        """
        Check whether the running fails.

        Returns:
            True/False
        """
        return len(self._results_raw['failed']) == 0 and len(self._results_raw['unreachable']) == 0


class ResultCallback(CallbackBase):
    """
    A sample callback plugin used for performing an action as results come in
    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def __init__(self):
        """
        Construct Function
        """
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_skipped = {}
        self._start_time = datetime.now()

    def v2_runner_on_ok(self, result):
        """
        Print a json representation of the result
        This method could store the result in an instance attribute for retrieval later
        Args:
            result (TaskResult): result information

        Returns:
            None
        """
        host_name = result._host.get_name()
        result_info = result._result
        self.host_ok[host_name] = {"task_name": result.task_name,
                                   "result": result_info}
        LOGGER.debug('==============v2_runner_on_ok======='
                     '==[task:%s]=========[host:%s]==============',
                     result.task_name, host_name)

        if result_info.get('changed', False):
            state = 'CHANGED'
        else:
            state = 'SUCCESS'

        LOGGER.debug("%s | %s => %s", host_name, state, result_info)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """
        Failure result output callback
        Args:
            result (TaskResult): result information
            ignore_errors (bool): Whether to ignore errors

        Returns:
            None
        """
        host_name = result._host.get_name()
        result_info = result._result

        LOGGER.debug('==============v2_runner_on_failed========='
                     '[task:%s]=========[host:%s]==============',
                     result.task_name, host_name)

        if 'exception' in result_info:
            # extract just the actual error message from the exception text
            error = result_info['exception'].strip().split('\n')[-1]
            LOGGER.error("An exception occurred during task execution. "
                         "To see the full traceback, use -vvv. The error was: %s", error)

        LOGGER.debug("%s | FAILED! => %s", host_name, result_info)
        if ignore_errors:
            LOGGER.info("... ignoring")
        else:
            self.host_failed[host_name] = {"task_name": result.task_name,
                                           "result": result_info}

    def v2_runner_on_unreachable(self, result):
        """
        Failure result output callback
        Args:
            result (TaskResult): result information

        Returns:
            None
        """
        host_name = result._host.get_name()
        result_info = result._result
        self.host_unreachable[host_name] = {"task_name": result.task_name,
                                            "result": result_info}

        LOGGER.debug('==============v2_runner_on_unreachable========='
                     '[task:%s]=========[host:%s]==============',
                     result.task_name, host_name)
        LOGGER.debug("%s | UNREACHABLE! => %s", host_name, result_info)

    def v2_runner_on_skipped(self, result):
        """
        Skipped result output callback
        Args:
            result (TaskResult): result information

        Returns:
            None
        """
        host_name = result._host.get_name()
        result_info = result._result
        self.host_skipped[host_name] = {"task_name": result.task_name,
                                        "result": result_info}
        LOGGER.debug('==============v2_runner_on_skipped========='
                     '[task:%s]=========[host:%s]==============',
                     result.task_name, host_name)
        LOGGER.debug("this task does not execute,please check parameter or condition.")
        LOGGER.debug("%s | SKIPPED! => %s", host_name, result_info)

    @staticmethod
    def _days_hours_minutes_seconds(runtime):
        """
        internal helper method for this callback
        Args:
            runtime (timedelta): run time

        Returns:
            run time in day (int), hour (int), minute (int), second (int)
        """
        minutes = (runtime.seconds // 60) % 60
        r_seconds = runtime.seconds - (minutes * 60)
        return runtime.days, runtime.seconds // 3600, minutes, r_seconds

    def v2_playbook_on_stats(self, stats):
        """
        Task running status method for this callback
        Args:
            stats (AggregateStats): stats of playbook

        Returns:
            None
        """
        runtime = datetime.now() - self._start_time
        runtime_count = self._days_hours_minutes_seconds(runtime)
        LOGGER.debug('==============play executes completed============'
                     '[use time:%s day %s h %s min %s s]==============',
                     runtime_count[0], runtime_count[1], runtime_count[2], runtime_count[3])

        hosts = sorted(stats.processed.keys())
        for host in hosts:
            summary = stats.summarize(host)

            LOGGER.debug(
                "%s : %s %s %s %s %s %s %s",
                hostcolor(host, summary),
                colorize('ok', summary['ok'], Constants.COLOR_OK),
                colorize('changed', summary['changed'], Constants.COLOR_CHANGED),
                colorize('unreachable',
                         summary['unreachable'], Constants.COLOR_UNREACHABLE),
                colorize('failed', summary['failures'], Constants.COLOR_ERROR),
                colorize('skipped', summary['skipped'], Constants.COLOR_SKIP),
                colorize('rescued', summary['rescued'], Constants.COLOR_OK),
                colorize('ignored', summary['ignored'], Constants.COLOR_WARN),
            )
