#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description: some helper function
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from aops_database.conf import configuration
from aops_database.factory.table import Base
from aops_utils.restful.status import DATABASE_CONNECT_ERROR, PARTIAL_SUCCEED,\
    SUCCEED


def make_mysql_engine_url():
    """
    Create engine url of mysql

    Returns:
        str: url of engine
    """
    mysql_host = configuration.mysql.get("IP")  # pylint: disable=E1101
    mysql_port = configuration.mysql.get("PORT")  # pylint: disable=E1101
    mysql_url_format = configuration.mysql.get("ENGINE_FORMAT")  # pylint: disable=E1101
    mysql_database_name = configuration.mysql.get("DATABASE_NAME")  # pylint: disable=E1101
    url = mysql_url_format % (mysql_host, mysql_port, mysql_database_name)
    return url


def create_database_engine(url, pool_size, pool_recycle):
    """
    Create database connection pool

    Args:
        url(str): engine url
        pool_size(int): size of pool
        pool_recycle(int): time that pool recycle the connection

    Returns:
        engine
    """
    engine = create_engine(url, pool_size=pool_size, pool_recycle=pool_recycle)
    return engine


engine_url = make_mysql_engine_url()
ENGINE = create_database_engine(engine_url,
                                configuration.mysql.get("POOL_SIZE"),  # pylint: disable=E1101
                                configuration.mysql.get("POOL_RECYCLE"))  # pylint: disable=E1101
SESSION = scoped_session(sessionmaker(bind=ENGINE))


def create_tables(engine):
    """
    Create all tables according to metadata of Base.

    Args:
        engine(instance): _engine.Engine instance
    """
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """
    Drop all tables according to metadata of Base.

    Args:
        engine(instance): _engine.Engine instance
    """
    Base.metadata.drop_all(engine)


def operate(proxy, data, func, session=None):
    """
    Database operation

    Args:
        proxy(proxy instance)
        data(dict)
        func(str): function name
        session(session or None): some database use session

    Returns:
        int: status code
    """

    if session is not None:
        if not proxy.connect(session):
            return DATABASE_CONNECT_ERROR
    else:
        if not proxy.connect():
            return DATABASE_CONNECT_ERROR

    function = getattr(proxy, func)
    res = function(data)
    proxy.close()
    return res


def judge_return_code(result, default_stat):
    """
    Generate return result according to result

    Args:
        result(dict)
        default_stat(int): default error status code

    Returns:
        int: status code
    """
    if (result.get('succeed_list') or result.get('update_list')):
        if result.get('fail_list'):
            return PARTIAL_SUCCEED
        else:
            return SUCCEED
    if result.get('fail_list'):
        return default_stat
    return SUCCEED


def combine_return_codes(default_stat, *args):
    """
    Combine multiple return codes into one code
    Args:
        default_stat: default error status code, if all codes in args are not success,
        will return default error code
        *args: multiple status code

    Returns:

    """
    if PARTIAL_SUCCEED in args:
        return PARTIAL_SUCCEED
    if SUCCEED in args:
        if len(set(args)) > 1:
            return PARTIAL_SUCCEED
        return SUCCEED
    return default_stat
