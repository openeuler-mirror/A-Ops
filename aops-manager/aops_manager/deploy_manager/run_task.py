#!/usr/bin/python3
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
Description: Running Deployment Tasks
Class: TaskRunner
"""
import os
import json
import yaml
from ansible.errors import AnsibleError
from aops_manager.deploy_manager.ansible_runner.ansible_runner import AnsibleRunner
from aops_manager.deploy_manager.config import TASKS_PATH, PLAYBOOK_PATH, INVENTORY_PATH
from aops_utils.log.log import LOGGER


class TaskRunner:
    """
    Run a task with orchestrated steps
    """

    @staticmethod
    def run_playbook(inventory_name, task_name, vault_password):
        """
        Run the playbook.
        Args:
            inventory_name (str): Host inventory file name
            task_name (str): task file name
            vault_password (str): password to decrypt host vars

        Returns:
            Whether the operation is successful
        """
        if vault_password is None:
            LOGGER.error("Invalid vault password")
            return False, None

        inventory_path = os.path.join(INVENTORY_PATH, task_name)
        if not os.path.exists(inventory_path):
            LOGGER.error("Invalid inventory file. %s", inventory_path)
            return False, None

        # Find the playbook and execute the ansible task.
        playbook_path = os.path.join(
            PLAYBOOK_PATH, "{}.yml".format(inventory_name))
        if not os.path.exists(playbook_path):
            LOGGER.error("Playbook not existed. %s", playbook_path)
            return False, None

        ansible_runner = AnsibleRunner(inventory_path, vault_password)
        ansible_runner.run_playbook(playbook_path)
        result = ansible_runner.get_result()
        LOGGER.debug(json.dumps(result, indent=4))
        ret = ansible_runner.no_failed()
        return ret, result

    @staticmethod
    def run_task(task_name=None, vault_password=None):
        """
        Executing a Deployment Task
        Args:
            task_name (str): task name. If this parameter is None, the default task is executed.
            vault_password (str): vault password to decrypt host vars
        Returns:
            True/False
        """
        # If task_name is None, the default task is executed.
        if not all([task_name, vault_password]):
            LOGGER.error("task_name or vault_password is None")
            return False

        task_file_path = os.path.join(TASKS_PATH, "{}.yml".format(task_name))
        if not os.path.exists(task_file_path):
            LOGGER.error("task_file not existed %s", task_file_path)
            return False
        with open(task_file_path, 'r', encoding='utf-8') as config_file:
            task_list = yaml.safe_load(config_file)
            if "step_list" not in task_list:
                LOGGER.error("Task %s has no step_list")
                return False

            # Traverse each step in the task list
            for step_name in task_list["step_list"]:
                step_info = task_list["step_list"][step_name]

                # If this step is not enabled, skip this step and go to the next step.
                if not step_info.get("enable", False):
                    LOGGER.warning(
                        "Task %s step %s is disabled, skip it", task_name, step_name)
                    continue

                need_continue = step_info.get("continue", False)

                try:
                    # Currently, the return details are not processed.
                    # The return progress function can be extended in the future.
                    ret = TaskRunner.run_playbook(step_name, step_name, vault_password)[0]
                except AnsibleError as exp:
                    LOGGER.error("ansible_runner exception:%s", exp)
                    ret = False

                # If you do not proceed to the next step after the failure, exit directly.
                if not need_continue and not ret:
                    return False

        return True
