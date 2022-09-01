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
import json
import time
from typing import NoReturn, List, Dict

from flask import Flask
from flask_apscheduler import APScheduler

from aops_check.mode import mode
from aops_check.mode.scheduler import Scheduler
from aops_check.conf import configuration
from aops_check.conf.constant import HOST_IP_INFO_LIST
from aops_check.utils.schema.default_mode import HostAddressSchema
from aops_check.core.rule.default_workflow import DefaultWorkflow
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import SUCCEED


class Util:
    @staticmethod
    def get_dict_from_file(file_path: str) -> List:
        """
            Get json data from file and return related list

        Args:
            file_path(str): the json data file absolute path
            file content structure: e.g
                {
                    'ip_list':[
                        {
                            "ip": "x.x.x.x",
                            "host": "xxxx"
                        }
                        ...
                    ]
                }

        Returns:
            List: e.g
                [
                    {
                        "ip": "x.x.x.x",
                        "host": "xxxx"
                    }
                ]
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

        except FileNotFoundError:
            LOGGER.error('Cannot find file /etc/aops/check_default.json when start aops-check '
                         'by default mode')
            raise FileNotFoundError("Cannot find file /etc/aops/check_default.json,"
                                    "please check it and try again")

        except json.decoder.JSONDecodeError:
            LOGGER.error('check_default json file content structure is not what we expect')
            raise ValueError("check_default file content structure is not what we expect "
                             "please check it and try again")

        if BaseResponse.verify_args(data, HostAddressSchema) != SUCCEED:
            LOGGER.error('The json data is not what we expect')
            raise ValueError("The data entered does not meet the requirements,please check the "
                             "data structure")

        return data['ip_list']

    @staticmethod
    def get_period_and_step():
        """
            get period and step from config file
        """
        period = configuration.default_mode.get('PERIOD')
        step = configuration.default_mode.get('STEP')

        if not period or not step:
            LOGGER.error("period or step may not be empty")
            raise ValueError("period or step may not be empty, please check it and try again!")

        if isinstance(period, int) and isinstance(step, int):
            return period, step
        raise ValueError("period or step is not composed of numbers!")

    @staticmethod
    def check_default_mode(ip_list: List[Dict[str, str]], time_range: List[int]) -> NoReturn:
        """
        Wrapper function about default mode.

        Args:
            ip_list(list): e.g
                    [
                        {
                            "ip": "x.x.x.x",
                            "host": "xxxx"
                        }
                    ]
            time_range(list): e.g
                    [1661862657, 1661862687]

        """
        wk = DefaultWorkflow(ip_list)
        wk.execute(time_range)


class Config:
    """
        Scheduled task configuration
    """
    JOBS = [
        {
            "id": "job_default",
            "func": "aops_check.mode.default_scheduler:Util.check_default_mode",
            "args": (Util.get_dict_from_file(HOST_IP_INFO_LIST),
                     [int(time.time()) - Util.get_period_and_step()[1], int(time.time())]),
            "trigger": "interval",
            "seconds": Util.get_period_and_step()[0],
        }
    ]


@mode.register('default')
class DefaultScheduler(Scheduler):
    """
    It's a default scheduler which loads default workflow and starts check.
    """

    @property
    def name(self) -> str:
        return "default"

    @staticmethod
    def run() -> NoReturn:
        app = Flask(__name__)
        app.config.from_object(Config())

        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        app.run(port=configuration.check.get('PORT'), host=configuration.check.get('IP'))
