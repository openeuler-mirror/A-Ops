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
Time: 2021-12-21 11:47:57
Author: peixiaochao
Description: functions about of database proxy
"""
import hmac
import base64
import time
import math
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import desc, asc

from aops_utils.restful.status import DATABASE_CONNECT_ERROR, PARTIAL_SUCCEED, SUCCEED


def make_mysql_engine_url(configuration):
    """
    Create engine url of mysql

    Args:
        configuration (Config): configuration object of certain module

    Returns:
        str: url of engine
    """
    mysql_host = configuration.mysql.get("IP")
    mysql_port = configuration.mysql.get("PORT")
    mysql_url_format = configuration.mysql.get("ENGINE_FORMAT")
    mysql_database_name = configuration.mysql.get("DATABASE_NAME")
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


def create_tables(base, engine, tables=None):
    """
    Create all tables according to metadata of Base.

    Args:
        base (instance): sqlalchemy.ext.declarative.declarative_base(), actually a registry instance
        engine(instance): _engine.Engine instance
        tables (list): table object list
    """
    base.metadata.create_all(engine, tables=tables)


def drop_tables(base, engine):
    """
    Drop all tables according to metadata of Base.

    Args:
        base (instance): sqlalchemy.ext.declarative.declarative_base(), actually a registry instance
        engine(instance): _engine.Engine instance
    """
    base.metadata.drop_all(engine)


def timestamp_datetime(value):
    """
    transfer unix time to formatted timestamp.

    Args:
        value (int): unix time.

    Returns:
        str: formatted time.
    """
    time_format = '%Y-%m-%dT%H:%M:%S%z'
    time_struct = time.localtime(value)
    return time.strftime(time_format, time_struct)


def timestr_unix(time_str):
    """
    transfer formatted timestamp to unix time.

    Args:
        time_str (str): formated time string.

    Returns:
        int: unix time.
    """
    time_format_with_hill = '%Y-%m-%dT%H:%M:%S.%f%z'

    time_str = time_str[:26] + time_str[-6:]
    time_format = time.strptime(time_str, time_format_with_hill)
    return int(time.mktime(time_format))


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


def sort_and_page(query_result, column, direction, per_page, page):
    """
    Sort and paginate the query result
    Args:
        query_result (sqlalchemy.orm.query.Query): query result
        column (sqlalchemy.orm.attributes.InstrumentedAttribute/
            sqlalchemy.sql.functions.count/None): the column that sort based on
        direction (str/None): desc or asc
        per_page (int/None): number of record per page, if per_page = None, return all
        page (int/None): which page to return, if page = None, return all

    Returns:
        sqlalchemy.orm.query.Query
    """
    total_page = 1
    total_count = len(query_result.all())

    if not total_count:
        return query_result, total_page

    direction = desc if direction == 'desc' else asc

    # when column is a sqlalchemy.sql.functions.count object, like func.count(Hots.host_id),
    # it has no boolean value, so "if column:" here is not available
    if column is not None:
        query_result = query_result.order_by(direction(column))

    if page and per_page:
        page = int(page)
        per_page = int(per_page)
        total_page = math.ceil(total_count / per_page)
        query_result = query_result.offset(
            (page - 1) * per_page).limit(per_page)

    return query_result, total_page


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


def generate_token(username, expire=3600):
    """
    generate token of username and expire time
    Args:
        username:
        expire:

    Returns:

    """
    time_str = str(time.time() + expire)
    time_byte = time_str.encode("utf-8")
    sha1_tester = hmac.new(username.encode(
        "utf-8"), time_byte, 'sha1').hexdigest()
    token = time_str + ':' + sha1_tester
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def certify_token(username, token):
    """
    certify token function
    Args:
        username(str): user name
        token(str): username and  expire time

    Returns(boolean): True if certify token is succeed else False

    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False

    ts_str = token_list[0]
    if float(ts_str) < time.time():
        # token expired
        return False

    known_sha1_taster = token_list[1]
    sha1 = hmac.new(username.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tests = sha1.hexdigest()
    if calc_sha1_tests != known_sha1_taster:
        # token certification failed
        return False

    # token certification success
    return True
