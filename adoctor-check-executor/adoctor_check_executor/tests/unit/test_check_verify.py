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
Author: YangYunYi
Date: 2021/9/1 22:16
docs: test_check_verify.py
description: test check verify
"""

import unittest
from adoctor_check_executor.common.check_verify import CheckTaskMsgSchema
from aops_utils.restful.response import MyResponse
from aops_utils.restful.status import SUCCEED


class TestCheckVerify(unittest.TestCase):
    def test_check_task_msg(self):
        test_data = {'task_id': -1, 'user': 'admin',
                     'host_list': [{'host_id': 'eca3b022070211ecab3ca01c8d75c8f3',
                                    'public_ip': '90.90.64.65'},
                                   {'host_id': 'f485bd26070211ecaa06a01c8d75c8f3',
                                    'public_ip': '90.90.64.64'},
                                   {'host_id': 'fa05c1ba070211ecad52a01c8d75c8f3',
                                    'public_ip': '90.90.64.66'}],
                     'check_items': [], 'time_range': [1630422091, 1630422121]}
        verify_res = MyResponse.verify_all(
            test_data, CheckTaskMsgSchema, "1234")
        self.assertEqual(verify_res, SUCCEED)


if __name__ == '__main__':
    unittest.main()
