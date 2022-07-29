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
Description: Some common functions are able to use in this project.
"""

import joblib
import numpy as np
import pandas as pd

from service.kafka import KafkaConsumer, KafkaProducer, EntityVariable
from service.prometheus import Prometheus
from utils.config_parser import ModelSettings, ServiceSettings
from utils.log import Log

log = Log().get_logger()


def load_prometheus_client() -> Prometheus:
    """
    Load and initialize the prometheus client.
    :return: The Prometheus client
    """
    settings = ServiceSettings()
    server = settings.prometheus_server
    port = settings.prometheus_port

    client = Prometheus(server, port)

    return client


def update_entity_variable():
    """
    Updates entity variables by querying data from Kafka under sub thread.
    :return: The sub thread.
    """
    log.info("Start to try updating global configurations by querying data from Kafka!")
    settings = ServiceSettings()

    server = settings.kafka_server
    port = settings.kafka_port
    topic = settings.kafka_consumer_topic

    sub_thread = KafkaConsumer(server, port, topic)
    sub_thread.start()

    return sub_thread


def update_service_settings(parser):
    """
    Update service settings globally
    :param parser: The arg parser
    :return: None
    """
    settings = ServiceSettings()
    settings.kafka_server = parser["kafka_server"]
    settings.kafka_port = parser["kafka_port"]
    settings.prometheus_server = parser["prometheus_server"]
    settings.prometheus_port = parser["prometheus_port"]


def most_contributions(x_pred: pd.DataFrame, y_pred: str):
    """
    Gets most contributed features based on pre-trained LR model.
    :param x_pred: The target X was used to predict.
    :param y_pred: The target y indicates the data label.
    :return:
    """
    top_n = 3

    pipe_lr_model = joblib.load("./file/pipe_lr_model.pkl")
    lr_coef = pipe_lr_model["clf"].coef_
    scaler = pipe_lr_model["scaler"]

    x_target = x_pred.iloc[y_pred == 1]
    contributions = np.mean(scaler.transform(x_target) * lr_coef, axis=0)
    top_index = contributions.argsort()[-top_n:][::-1]
    column_names = x_target.columns[top_index]

    return list(column_names)


def data_norm(x):
    """
    Data normalization based on normalization model.
    :param x: The training data X
    :return: The normalized data X_norm
    """
    settings = ModelSettings()
    props = settings.norm_properties
    path = props["path"]
    norm_model = joblib.load(path)
    x_norm = norm_model.transform(x).astype(np.float32)
    return x_norm


def save_normalizer(norm_model):
    """
    Saving Normalizer to the file.
    :param norm_model: The normalizer model
    :return: None
    """
    settings = ModelSettings()
    props = settings.norm_properties
    path = props["path"]
    joblib.dump(norm_model, path)


def get_kafka_message(timestamp, y_pred, metric_label, recommend_metrics):
    """
    Generates the Kafka message based the parameters.
    :param timestamp: The time stamp
    :param y_pred: The predicted label
    :param metric_label: The metric label dict contains metadate info
    :param recommend_metrics: The recommend metrics
    :return: The aggregated messages
    """
    variable = EntityVariable.variable.copy()

    machine_id = metric_label["machine_id"]
    table_name = variable["meta_name"]
    keys = []
    filtered_metric_label = {}
    for key in variable["keys"]:
        filtered_metric_label[key] = metric_label[key]
        if key in metric_label and key != "machine_id":
            keys.append(metric_label[key])

    entity_id = f"{machine_id}_{table_name}_{'_'.join(keys)}"

    sample_count = len(y_pred)
    if sample_count != 0:
        anomaly_score = sum(y_pred) / sample_count
    else:
        anomaly_score = 0

    message = {
        "Timestamp": timestamp,
        "Attributes": {
            "Entity_ID": entity_id
        },
        "Resource": {
            "anomaly_score": anomaly_score,
            "anomaly_count": sum(y_pred),
            "total_count": len(y_pred),
            "duration": 60,
            "anomaly_ratio": anomaly_score,
            "metric_label": filtered_metric_label,
            "recommend_metrics": recommend_metrics,
            "metric_id": "gala_gopher_redis_client_recent_rtt",
        },
        "SeverityText": "WARN",
        "SeverityNumber": 14,
        "Body": "I'am a abnormal event.",
        "client_ip": metric_label.get("client_ip", ""),
        "server_ip": metric_label.get("server_ip", ""),
        "server_port": metric_label.get("server_port", ""),
        "abnormal_metric": "simulated_gala_gopher_redis_client_recent_rtt",
    }

    return message


def sent_message_to_kafka(value: str):
    """
    Sent message to kafka
    :param value: the message
    :return: None
    """
    settings = ServiceSettings()

    server = settings.kafka_server
    port = settings.kafka_port
    topic = settings.kafka_procedure_topic

    kafka_producer = KafkaProducer(server, port)
    kafka_producer.send_message(topic, value)
    log.info(f"Abnormal events were detected, and sent the message to Kafka!")
