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
Description: callback function of the cve task.
"""
from collections import defaultdict
from ansible.plugins.callback import CallbackBase

from aops_utils.log.log import LOGGER


class TaskCallback(CallbackBase):
    """
    Callback function for cve task.
    """

    def __init__(self, task_id, proxy, task_info):
        """
        Args:
            task_id (str): the current task id
            proxy (object): database proxy
            task_info (dict): host info or some specific task info
        """
        self.result = defaultdict(dict)
        self.check_result = defaultdict(dict)
        self.task_id = task_id
        self.proxy = proxy
        self.task_info = task_info
        super().__init__()

    @staticmethod
    def _get_info(result):
        """
        Get the running task info from the ansible result.

        Args:
            result (object): result class of the ansible

        Returns:
            str: host name of the current sub task
            dict: result information
            str: name of the sub task
        """
        # The parameter:result is the only result that we can get from ansible,
        # since we need to get task info, it's inevitable to access its private
        # member.
        host_name = result._host.get_name()  # pylint: disable=W0212
        result_info = result._result  # pylint: disable=W0212
        task_name = result.task_name

        return host_name, result_info, task_name

    def _record_info(self, result, status):
        """
        Get task info and record the result.

        Args:
            result (object): result class of the ansible
            status (str): task status

        Returns:
            str: host name of the sub task
            str: name of the sub task
        """

        host_name, result_info, task_name = self._get_info(result)
        self.result[host_name][task_name] = {
            "info": result_info.get('stdout') or\
                    result_info.get('stderr') or\
                    result_info.get('msg'),
            "status": status
            }

        LOGGER.debug("task id: %s, task name: %s, host name: %s, result: %s",
                     self.task_id, task_name, host_name, status)
        return host_name, task_name
