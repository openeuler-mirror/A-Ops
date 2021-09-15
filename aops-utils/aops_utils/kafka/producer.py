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
Base kafka producer
"""
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

from aops_utils.log.log import LOGGER
from aops_utils.kafka.kafka_exception import ProducerInitError


__all__ = ["BaseProducer"]


class BaseProducer:
    """
    Producer of kafka, split job into msgs
    """
    def __init__(self, configuration):
        """
        Init kafka's producer and topic based on config
        Args:
            configuration (aops_utils.conf.Config object): config object of producer's config file

        Raises: ProducerInitError

        """
        try:
            self.conf = {
                "value_serializer": lambda v: json.dumps(v).encode('utf-8'),
                "key_serializer": lambda v: json.dumps(v).encode('utf-8'),
                "bootstrap_servers": configuration.producer["KAFKA_SERVER_LIST"],
                "api_version": configuration.producer["API_VERSION"],
                "acks": configuration.producer["ACKS"],
                "retries": configuration.producer["RETRIES"],
                "retry_backoff_ms": configuration.producer["RETRY_BACKOFF_MS"]
            }
            self._producer = KafkaProducer(**self.conf)
        except (TypeError, AttributeError, KeyError) as err:
            LOGGER.error("Producer init failed with wrong config file. %s", err)
            raise ProducerInitError("Producer init failed with wrong config file.") from err
        except KafkaError as err:
            LOGGER.error("Producer init failed with internal error. %s", err)
            raise ProducerInitError("Producer init failed with internal error.") from err

    def bootstrap_connected(self):
        """
        if bootstrap is connected
        Returns:
            bool
        """
        return self._producer.bootstrap_connected()

    def close(self):
        """
        close the producer
        Returns:
            None
        """
        self._producer.close()

    def flush(self):
        """
        send messages left in cache
        Returns:
            None
        """
        self._producer.flush()

    @staticmethod
    def _send_success(record_metadata):
        """
        callback function for successful message sending
        Args:
            record_metadata (record_metadata): message's topic, partition and offset
        """
        LOGGER.debug("Sent successfully. Topic: %s, Partition: %s, Offset: %s",
                     record_metadata.topic, record_metadata.partition, record_metadata.offset)

    @staticmethod
    def _send_failed(excp):
        """
        callback function for failed message sending
        Args:
            excp (exception): exception of sending message
        """
        LOGGER.error("Send failed.", exc_info=excp)

    def send_msg(self, topic, value, key=None, partition=None):
        """
        send one message into broker
        Args:
            topic (str): topic of the message
            value (dict): value of the message
            key (str): messages with same key will be sent to same partition
            partition (str): random if not specified

        """
        if not value:
            return
        kwargs = {
            "value": value,
            "key": key,
            "partition": partition
        }
        try:
            self._producer.send(topic, **kwargs)\
                .add_callback(BaseProducer._send_success).add_errback(BaseProducer._send_failed)
        except KafkaError as err:
            LOGGER.error(err)
