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
Description: The Config Parser to load and parse the global settings from .ini file.
"""
import configparser
import os
from functools import wraps

from anteater.utils.singleton import Singleton


def validate_properties(section: str, key: str = None):
    """
    Decorator factory for validating the section name
    and the key name in service.settings.ini.

    :param section: The section name
    :param key: The key name
    :return: The decorator factory.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            self = args[0]
            self.validate(section, key)
            return func(self)
        return wrapper
    return decorator


class Settings(metaclass=Singleton):
    """
    The Settings Config Class which illustrates some global
    settings configuration parsed from *.settings.ini file.
    """
    def __init__(self):
        self.config = None
        self.sections = None

    def load(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        self.config = config
        self.sections = config.sections()

    def validate(self, section, key):
        if section not in self.sections:
            raise ValueError(f"Unknown section {section}!")
        if key is not None and key not in self.config[section]:
            raise ValueError(f"Unknown key name {key} in section {section}!")

    def update_keys(self, section, key, value):
        self.validate(section, key)
        self.config[section][key] = value


class ServiceSettings(Settings):
    """
    The settings for service level.
    """
    def __init__(self):
        super().__init__()
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        file_path = os.path.join(root_path, "configuration" + os.sep + "service.settings.ini")
        self.load(file_path)

    @property
    @validate_properties("Kafka", "server")
    def kafka_server(self):
        return self.config["Kafka"]["server"]

    @kafka_server.setter
    def kafka_server(self, value):
        self.config["Kafka"]["server"] = value

    @property
    @validate_properties("Kafka", "port")
    def kafka_port(self):
        return self.config["Kafka"]["port"]

    @kafka_port.setter
    def kafka_port(self, value):
        self.config["Kafka"]["port"] = value

    @property
    @validate_properties("KafkaProducer", "topic")
    def kafka_procedure_topic(self):
        return self.config["KafkaProducer"]["topic"]

    @property
    @validate_properties("KafkaConsumer", "topic")
    def kafka_consumer_topic(self):
        return self.config["KafkaConsumer"]["topic"]

    @property
    @validate_properties("Prometheus", "server")
    def prometheus_server(self):
        return self.config["Prometheus"]["server"]

    @prometheus_server.setter
    def prometheus_server(self, value):
        self.config["Prometheus"]["server"] = value

    @property
    @validate_properties("Prometheus", "port")
    def prometheus_port(self):
        return self.config["Prometheus"]["port"]

    @prometheus_port.setter
    def prometheus_port(self, value):
        self.config["Prometheus"]["port"] = value


class ModelSettings(Settings):
    """
    The settings for model level.
    """
    def __init__(self):
        super().__init__()
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        file_path = os.path.join(root_path, "configuration" + os.sep + "model.settings.ini")
        self.load(file_path)

    @property
    @validate_properties("HybridModel")
    def hybrid_properties(self) -> dict:
        return dict(self.config["HybridModel"])

    @property
    @validate_properties("RandomForest")
    def rf_properties(self) -> dict:
        return dict(self.config["RandomForest"])

    @property
    @validate_properties("VAE")
    def vae_properties(self) -> dict:
        return dict(self.config["VAE"])

    @property
    @validate_properties("Normalization")
    def norm_properties(self) -> dict:
        return dict(self.config["Normalization"])

    @property
    @validate_properties("Normalization")
    def norm_properties(self) -> dict:
        return dict(self.config["Normalization"])
