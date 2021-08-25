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
Base kafka consumer
"""
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from aops_utils.log.log import LOGGER
from aops_utils.kafka.kafka_exception import ConsumerInitError


__all__ = ["BaseConsumer"]


class BaseConsumer:
    """
    Consumer of kafka
    """
    def __init__(self, topic, group_id, configuration):
        """
        Init consumer
        Args:
            topic (str): Consumer's topic
            group_id (str): Consumer group's id
            configuration (aops_utils.conf.Config object): config object of consumer's config file

        Raises: ConsumerInitError

        """
        try:
            self.topic = topic
            self.conf = {
                "value_deserializer": lambda v: json.loads(v.decode('utf-8')),
                "key_deserializer": lambda v: json.loads(v.decode('utf-8')),
                "bootstrap_servers": configuration.consumer["KAFKA_SERVER_LIST"],
                "group_id": group_id,
                "enable_auto_commit": configuration.consumer["ENABLE_AUTO_COMMIT"],
                "auto_offset_reset": configuration.consumer["AUTO_OFFSET_RESET"]
            }
            self.timeout_ms = configuration.consumer["TIMEOUT_MS"]
            self.max_records = configuration.consumer["MAX_RECORDS"]
            self._consumer = KafkaConsumer(self.topic, **self.conf)
        except (TypeError, AttributeError, KeyError) as err:
            LOGGER.error("Consumer init failed with wrong config file. %s", err)
            raise ConsumerInitError("Consumer init failed with wrong config file.") from err
        except KafkaError as err:
            LOGGER.error("Consumer init failed with internal error. %s", err)
            raise ConsumerInitError("Consumer init failed with internal error.") from err

    def poll(self):
        """
        poll message from broker
        Returns:

        """
        return self._consumer.poll(timeout_ms=self.timeout_ms, max_records=self.max_records)

    def bootstrap_connected(self):
        """
        Return True if the bootstrap is connected.
        Returns:
            bool
        """
        return self._consumer.bootstrap_connected()

    def close(self):
        """
        Close the consumer, waiting indefinitely for any needed cleanup
        Returns:
            None
        """
        self._consumer.close()

    def commit(self):
        """
        Commit offsets to kafka, blocking until success or error.
        Returns:
            None
        """
        self._consumer.commit()
