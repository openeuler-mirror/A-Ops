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
from aops_check.conf import configuration
from aops_check.database.dao.app_dao import AppDao
from aops_check.database.factory.mapping import MAPPINGS


def init_es():
    dao = AppDao(configuration=configuration)
    if not dao.connect():
        raise ElasticsearchException("connect to elasticsearch fail")

    for index_name, body in MAPPINGS.items():
        res = dao.create_index(index_name, body)
        if not res:
            raise ElasticsearchException("create elasticsearch index %s fail", index_name)

    LOGGER.info("create check related elasticsearch index succeed")
