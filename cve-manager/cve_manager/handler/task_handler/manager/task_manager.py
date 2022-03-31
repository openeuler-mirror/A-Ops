#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
Time:
Author:
Description: ansible runner
"""
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible import context
from ansible.errors import AnsibleError

from aops_utils.log.log import LOGGER


class CveAnsible():
    """
    Ansible task manager.
    """

    def __init__(self,
                 connection='smart',
                 remote_user=None,
                 remote_password=None,
                 private_key_file=None,
                 sudo=None,
                 sudo_user=None,
                 ask_sudo_pass=None,
                 module_path=None,
                 become=None,
                 become_method=None,
                 become_user=None,
                 listhosts=None,
                 listtasks=None,
                 listtags=None,
                 verbosity=3,
                 syntax=None,
                 start_at_task=None,
                 inventory=None,
                 callback=None,
                 vault_password=None):
        """
        initialization
        """
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            private_key_file=private_key_file,
            become=become,
            become_method=become_method,
            become_user=become_user,
            sudo=sudo,
            sudo_user=sudo_user,
            ask_sudo_pass=ask_sudo_pass,
            module_path=module_path,
            listhosts=listhosts,
            verbosity=verbosity,
            listtasks=listtasks,
            listtags=listtags,
            syntax=syntax,
            start_at_task=start_at_task
        )
        self.inventory = inventory
        self.vault_password = vault_password
        self.passwords = remote_password
        self.results_callback = callback

        # initialize needed objects
        self.loader = DataLoader()
        # create inventory
        self.inventory_manager = InventoryManager(
            loader=self.loader, sources=inventory)
        # create variable manager
        self.variable_manager = VariableManager(
            loader=self.loader, inventory=self.inventory_manager)

    @property
    def result(self):
        """
        Return the result.

        Returns:
            dict
        """
        return self.results_callback.result

    @property
    def check(self):
        """
        Return the check result.

        Returns:
            dict
        """
        return self.results_callback.check_result

    @property
    def info(self):
        """
        Return the task info.

        Returns:
            dict
        """
        return self.results_callback.task_info

    def playbook(self, playbook):
        """
        Execute playbooks

        Args:
            playbook (list): path of playbook

        Returns:
            bool
        """
        executor = PlaybookExecutor(
            playbooks=playbook,
            inventory=self.inventory_manager,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords
        )
        executor._tqm._stdout_callback = self.results_callback

        try:
            executor.run()
            return True
        except AnsibleError as error:
            LOGGER.error(error)
            return False
