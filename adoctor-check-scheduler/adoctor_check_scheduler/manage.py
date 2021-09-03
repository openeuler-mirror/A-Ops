#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
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
Date: 2021/8/4 17:20
docs: check_scheduler_manager.py
description: check scheduler manager
"""
import sys
from flask import Flask
from flask_apscheduler import APScheduler
import adoctor_check_scheduler
from adoctor_check_scheduler.common.config import scheduler_check_config
from adoctor_check_scheduler.common.check_consumer import RetryTaskConsumer
from adoctor_check_scheduler.common.constant import CheckTopic, CheckGroup
from adoctor_check_scheduler.check_scheduler.task_manager import check_task_manager

consumers = []


def init_app():
    """
    Check service manager.
    """
    app = Flask(__name__)
    apscheduler = APScheduler()
    apscheduler.init_app(app)
    apscheduler.start()

    # register blue print
    for blue, api in adoctor_check_scheduler.blue_point:
        api.init_app(app)
        app.register_blueprint(blue)

    # Adding a Scheduled Task
    check_task_manager.add_timed_task(app)

    return app

def start_retry_task():
    # Start retry task consumer
    retry_task_consumer = RetryTaskConsumer(CheckTopic.retry_check_topic,
                                            CheckGroup.retry_check_group_id,
                                            scheduler_check_config)
    consumers.append(retry_task_consumer)
    retry_task_consumer.start()


def stop_check_scheduler():
    for consumer in consumers:
        consumer.stop_consumer()


start_retry_task()
app = init_app()


if __name__ == "__main__":
    # Start app
    check_ip = scheduler_check_config.service['IP']
    check_port = scheduler_check_config.service['PORT']
    app.run(port=check_port, host=check_ip)
