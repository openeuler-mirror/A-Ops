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
from datetime import datetime, timezone
from functools import partial
from typing import Dict

from apscheduler.schedulers.blocking import BlockingScheduler

from anteater.model.hybrid_model import HybridModel
from anteater.model.key_metric_model import KeyMetricModel
from anteater.model.post_model import PostModel
from anteater.service.kafka import EntityVariable
from anteater.utils.common import update_entity_variable, sent_to_kafka, get_kafka_message, update_service_settings
from anteater.utils.log import Log

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


def anomaly_detection(hybrid_model, key_metric_model, post_model, parser: Dict[str, any]):
    """Run anomaly detection model periodically"""
    utc_now = datetime.now(timezone.utc).astimezone().replace(second=0, microsecond=0)

    if not EntityVariable.variable:
        log.info("Configuration hasn't been updated.")
        return

    log.info(f"START: run anomaly detection model.")

    machine_ids, dfs = hybrid_model.get_inference_data(utc_now)

    for machine_id, df in zip(machine_ids, dfs):
        if df.shape[0] == 0:
            log.warning(f"Not data was founded for the target machine {machine_id}, please check it first!")

        y_pred = hybrid_model.predict(df)
        is_abnormal = hybrid_model.is_abnormal(y_pred)
        if is_abnormal:
            key_metric_anomalies = key_metric_model.detect_key_metric(utc_now, machine_id)
            rec_anomalies = post_model.top_n_anomalies(utc_now, machine_id, top_n=30)
            for anomalies in key_metric_anomalies:
                msg = get_kafka_message(round(utc_now.timestamp()), y_pred.tolist(),
                                        machine_id, anomalies, rec_anomalies)
                sent_to_kafka(msg)
            log.info(f"END: abnormal events were detected on machine {machine_id}, sent the message to Kafka!")
        else:
            log.info(f"END: no abnormal events on machine {machine_id}.")


def main():
    utc_now = datetime.now(timezone.utc).astimezone().replace(second=0, microsecond=0)
    log.info("Run gala_anteater main function...")

    parser = arg_parser()
    update_service_settings(parser)
    sub_thread = update_entity_variable()

    hybrid_model = HybridModel()
    key_metric_model = KeyMetricModel()
    post_model = PostModel()

    if parser["retrain"]:
        log.info("Start to re-train the model based on last day metrics dataset!")
        x = hybrid_model.get_training_data(utc_now)
        hybrid_model.training(x)

    log.info(f"Schedule recurrent job with time interval {parser['duration']} minute(s).")
    scheduler = BlockingScheduler()
    scheduler.add_job(partial(anomaly_detection, hybrid_model, key_metric_model, post_model, parser),
                      parser["trigger_type"], minutes=1)
    scheduler.start()

    sub_thread.join()


if __name__ == '__main__':
    main()
