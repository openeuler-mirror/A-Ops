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
Time:
Author:
Description:
"""
import time
import unittest

from aops_manager.database.proxy.host import HostInfoProxy
from aops_manager.conf.constant import HOST_INFO_INDEX
from aops_manager.conf import configuration
from aops_utils.restful.status import SUCCEED


class TestHostInfoDatabase(unittest.TestCase):
    def setUp(self):
        # create engine to database
        host = "127.0.0.1"
        port = 9200
        self.proxy = HostInfoProxy(configuration, host, port)
        self.proxy.connect()
        self.proxy.delete_index(HOST_INFO_INDEX)

    def tearDown(self):
        self.proxy.delete_index(HOST_INFO_INDEX)
        self.proxy.close()

    def test_api_host_info(self):
        # ==============save host info===================
        data = {
            "host_infos": [
                {
                    "host_id": "id1",
                    "infos": {
                        "cpu": {
                            "count": 96
                        }
                    }
                },
                {
                    "host_id": "id2",
                    "infos": {
                        "memory": {
                            "size": "256G"
                        }
                    }
                }
            ]
        }
        res = self.proxy.save_host_info(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)
        # ===============get host info=====================
        data = {
            "host_list": ["id1", "id2"]
        }
        res = self.proxy.get_host_info(data)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(len(res[1]['host_infos']), 2)

        # ===============delete host info=====================
        data = {
            "host_list": ["id1", "id2"]
        }
        res = self.proxy.delete_host_info(data)
        self.assertEqual(res, SUCCEED)
        time.sleep(1)

        res = self.proxy.get_host_info(data)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(len(res[1]['host_infos']), 0)
