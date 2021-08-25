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
Description: Self-defined Exception class
"""


class ProducerInitError(Exception):
    """
    Self-defined consumer init failed exception
    """
    def __init__(self, error_info=''):
        super().__init__(self)
        self.message = error_info

    def __str__(self):
        return self.message


class ConsumerInitError(Exception):
    """
    Self-defined consumer init failed exception
    """
    def __init__(self, error_info=''):
        super().__init__(self)
        self.message = error_info

    def __str__(self):
        return self.message
