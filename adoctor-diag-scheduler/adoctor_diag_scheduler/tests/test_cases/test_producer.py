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
import unittest
from unittest import mock

from adoctor_diag_scheduler.function.producer import Producer
from adoctor_diag_scheduler.conf import diag_configuration


class TestProducer(unittest.TestCase):

    @mock.patch.object(Producer, "send_msg")
    @mock.patch("adoctor_diag_scheduler.function.helper.get_tree_from_database")
    def test_producer(self, mock_get_tree_from_database, mock_send_msg):
        mock_get_tree_from_database.side_effect = [{"tree1": {"name": "tree1"}},
                                                    {"tree2": {"name": "tree2"}}]
        mock_send_msg.side_effect = [None] * 84

        job_dict = {
                    "username": "admin",
                    "host_list": ["host1", "host2"],
                    "time_range": [11246, 12456],
                    "tree_list": ["tree1", "tree2"],
                    "interval": 60
                }
        producer = Producer(diag_configuration)
        task_id, jobs_num = producer.create_msgs(job_dict)
        self.assertEqual(jobs_num, 84)
        self.assertNotIn("-", task_id)
