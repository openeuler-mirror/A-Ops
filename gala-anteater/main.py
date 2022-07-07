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
Description: The main function of gala-anteater project.
"""

import argparse
from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Dict

from apscheduler.schedulers.blocking import BlockingScheduler

from model.base import Predict
from model.vae import VAEPredict
from service.kafka import EntityVariable
from source.metrics import MetricsLoader, get_training_data
from utils.common import update_entity_variable, most_contributions, data_norm, sent_message_to_kafka, \
    get_kafka_message, update_service_settings
from utils.log import Log
from utils.select_model import select_model

log = Log().get_logger()


def arg_parser():
    parser = argparse.ArgumentParser(
        description="gala-anteater project for operation system KPI metrics anomaly detection")

    parser.add_argument("-ks", "--kafka_server",
                        help="The kafka server ip", type=str, required=True)
    parser.add_argument("-kp", "--kafka_port",
                        help="The kafka server port", type=str,  required=True)
    parser.add_argument("-ps", "--prometheus_server",
                        help="The prometheus server ip", type=str, required=True)
    parser.add_argument("-pp", "--prometheus_port",
                        help="The prometheus server port", type=str, required=True)
    parser.add_argument("-m", "--model",
                        help="The machine learning model - random_forest, vae",
                        type=str, default="random_forest", required=False)
    parser.add_argument("-ty", "--trigger_type",
                        help="The scheduling type of anomaly detection task",
                        type=str, default='interval', required=False)
    parser.add_argument("-d", "--duration",
                        help="The time interval of scheduling anomaly detection task (minutes)",
                        type=int, default=1, required=False)
    parser.add_argument("-rt", "--retrain",
                        help="If retrain the vae model or not",
                        type=bool, default=False, required=False)
    arguments = vars(parser.parse_args())

    return arguments


def anomaly_detection(model: Predict, parser: Dict[str, any]):
    utc_now = datetime.now(timezone.utc).astimezone().replace(second=0, microsecond=0)

    start = utc_now - timedelta(minutes=parser["duration"])
    end = utc_now

    if not EntityVariable.variable:
        log.info("Configuration hasn't been updated!")
        return

    log.info(f"{utc_now}: start to run anomaly detection model...")
    metrics_loader = MetricsLoader(start, end)
    features = metrics_loader.extract_features()

    for unique_id, data_frame in features:
        x_norm = data_norm(data_frame)
        y_pred = model.predict(x_norm)
        is_abnormal = model.is_abnormal(y_pred)
        if is_abnormal:
            recommend_metrics = most_contributions(data_frame, y_pred)

            msg = get_kafka_message(round(utc_now.timestamp()), y_pred, unique_id, recommend_metrics)

            sent_message_to_kafka(msg)
            log.info(f"{utc_now}: Abnormal events were detected, sent the message to Kafka!")
        else:
            log.info(f"{utc_now}: NO abnormal events.")


def main():
    log.info("Run gala_anteater main function...")

    parser = arg_parser()
    update_service_settings(parser)
    sub_thread = update_entity_variable()

    model_name = parser["model"]
    model = select_model(model_name)

    if isinstance(model, VAEPredict) and parser["retrain"]:
        log.info("Start to re-train the vae model based on last day metrics dataset!")
        x = get_training_data()
        model.training(x)

    log.info(f"Schedule recurrent job with time interval {parser['duration']} minute(s).")
    scheduler = BlockingScheduler()
    scheduler.add_job(partial(anomaly_detection, model, parser), parser["trigger_type"], minutes=parser["duration"])
    scheduler.start()

    sub_thread.join()


if __name__ == '__main__':
    main()
