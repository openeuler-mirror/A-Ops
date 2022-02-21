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
Description:
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from aops_utils.database.helper import make_mysql_engine_url
from aops_utils.database.helper import create_database_engine
from aops_manager.conf import configuration


engine_url = make_mysql_engine_url(configuration)
ENGINE = create_database_engine(engine_url,
                                configuration.mysql.get("POOL_SIZE"),  # pylint: disable=E1101
                                configuration.mysql.get("POOL_RECYCLE"))  # pylint: disable=E1101
SESSION = scoped_session(sessionmaker(bind=ENGINE))
