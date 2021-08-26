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
Test BaseConsumer init (basically read config)
"""
import os
import unittest
from aops_utils.conf import Config
from aops_utils.kafka.producer import BaseProducer
from aops_utils.kafka.kafka_exception import ProducerInitError


__here__ = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(__here__, "../data/")


class TestConsumerInit(unittest.TestCase):
    """
    Test Consumer init with specific configuration
    """

    def test_miss_config(self):
        miss_config_path = os.path.join(data_path, "miss_key_producer_config.ini")
        configuration = Config(miss_config_path)
        with self.assertRaises(ProducerInitError) as context:
            producer = BaseProducer(configuration)
            producer.close()
        self.assertTrue("Producer init failed with wrong config file." in str(context.exception))

    def test_none_configfile(self):
        right_config_path = os.path.join(data_path, "none_config.ini")
        configuration = Config(right_config_path)
        with self.assertRaises(ProducerInitError) as context:
            producer = BaseProducer(configuration)
            producer.close()
        self.assertTrue("Producer init failed with wrong config file." in str(context.exception))

    def test_right_config(self):
        right_config_path = os.path.join(data_path, "right_producer_config.ini")
        configuration = Config(right_config_path)

        producer = BaseProducer(configuration)
        producer.bootstrap_connected()
        self.assertFalse(producer.bootstrap_connected())
