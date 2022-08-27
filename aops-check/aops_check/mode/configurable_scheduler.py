#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
from typing import NoReturn

from flask import Flask
from flask_apscheduler import APScheduler
from aops_check import BLUE_POINT
from aops_check.conf import configuration
from aops_check.init import init
from aops_check.mode import mode
from aops_check.mode.scheduler import Scheduler
from aops_check.core.check.check_scheduler.check_scheduler import check_scheduler

@mode.register('configurable')
class ConfigurableScheduler(Scheduler):
    """
    It's a configurable scheduler which needs to configure workflow and app, then start check.
    """

    @property
    def name(self) -> str:
        return "configurable"

    @staticmethod
    def run() -> NoReturn:
        """
        Init elasticsearch and run a flask app.
        """
        init()

        app = Flask(__name__)
        apscheduler = APScheduler()
        apscheduler.init_app(app)
        apscheduler.start()

        for blue, api in BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        check_scheduler.start_all_workflow(app)
        ip = configuration.check.get('IP')
        port = configuration.check.get('PORT')
        app.run(port=port, host=ip)
