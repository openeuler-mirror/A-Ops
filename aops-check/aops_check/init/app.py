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
from elasticsearch import ElasticsearchException

from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATA_EXIST, SUCCEED
from aops_check.conf import configuration
from aops_check.core.experiment.app.network_diagnose import NetworkDiagnoseApp
from aops_check.database.dao.app_dao import AppDao

default_app = [
    NetworkDiagnoseApp
]


def init_app():
    dao = AppDao(configuration=configuration)
    if not dao.connect():
        raise ElasticsearchException("connect to elasticsearch fail")

    for app in default_app:
        info = app().info
        status_code = dao.create_app(info)
        if status_code == DATA_EXIST:
            LOGGER.warning(
                f"The app {info['app_name']} has existed, choose to ignore")
        elif status_code != SUCCEED:
            LOGGER.error(f"Import default app {info['app_name']} fail")

    LOGGER.info("Import default app done")
