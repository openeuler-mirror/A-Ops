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
producer class for producing diagnose messages
"""

import uuid
from itertools import product

from aops_utils.log.log import LOGGER
from aops_utils.kafka.producer import BaseProducer
from adoctor_diag_scheduler.function.helper import get_validate_hosts, \
    get_trees_content, get_time_slices, save_task


class Producer(BaseProducer):
    """
    Producer of kafka, split job into msgs
    """
    def __init__(self, configuration):
        """
        Init kafka's producer and topic based on config
        """
        super().__init__(configuration)
        self.topic = configuration.topic.get("NAME")

    @staticmethod
    def _create_task_id():
        """
        create uuid without "-" because of elasticsearch restriction
        Returns:
            str
        """
        raw_uuid = str(uuid.uuid1())
        reformat_uuid = raw_uuid.replace("-", "")
        return reformat_uuid

    def create_msgs(self, job_info):
        """
        split job and send messages
        Args:
            job_info (dict): job's info from request, example:
                {
                    "username": "admin",
                    "host_list": ["host1", "host2"],
                    "time_range": [ts1, ts2],
                    "tree_list": ["tree1", "tree2"],
                    "interval": 60
                }
        Returns:
            str, int: task id and total jobs number.

        Raises: KeyError

        """
        # convert time range into int. The verify schema is not that good to get rid of
        # string type int like "111".
        time_range = [int(job_info['time_range'][0]), int(job_info['time_range'][1])]
        # split time range based on interval
        time_slices = get_time_slices(time_range, int(job_info['interval']))

        # get validate host from database
        hosts = get_validate_hosts(job_info['host_list'], job_info["username"])
        # get validate trees' content from database
        tree_dict = get_trees_content(job_info['tree_list'], job_info["username"])

        val_trees = tree_dict.keys()
        jobs_num = len(hosts) * len(val_trees) * len(time_slices)

        if jobs_num == 0:
            return None, 0

        job_info['host_list'] = hosts
        job_info['tree_list'] = list(val_trees)
        task_id = Producer._create_task_id()

        for host, val_tree, time_slice in product(hosts, val_trees, time_slices):
            msg = {"username": job_info["username"], "host_id": host,
                   "time_range": time_slice, "tree_name": val_tree,
                   "tree_content": tree_dict[val_tree], "task_id": task_id}
            self.send_msg(self.topic, msg)

        # send msgs in cache
        self._producer.flush()
        self._producer.close()
        LOGGER.info("%d kafka messages created." % jobs_num)

        save_task(job_info, task_id, jobs_num)

        return task_id, jobs_num
