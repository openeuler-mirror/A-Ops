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
import requests
from flask import jsonify, json, Response

from aops_manager.account_manager.cache import UserCache
from aops_manager.database import SESSION
from aops_manager.database.proxy.host import HostProxy
from aops_manager.function.verify.agent import AgentPluginInfoSchema
from aops_manager.conf.constant import ROUTE_AGENT_PLUGIN_INFO
from aops_utils.database.table import Host
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import (
    make_response,
    TOKEN_ERROR,
    SUCCEED,
    HTTP_CONNECT_ERROR,
    NO_DATA,
    DATABASE_CONNECT_ERROR,
    StatusCode
)


class AgentUtil:

    @classmethod
    def get_host_ip(cls, host_id: str) -> tuple:
        """
            get host ip from database by host id

        Args:
            host_id(str)

        Returns:
            tuple: host ip, status code
        """
        proxy = HostProxy()
        if proxy.connect(SESSION):
            query_res = proxy.session.query(
                Host).filter_by(host_id=host_id).all()
            if len(query_res) == 0:
                LOGGER.error("no such host_id, please check.")
                return '', NO_DATA
            proxy.close()
        else:
            LOGGER.error("connect to database error")
            return '', DATABASE_CONNECT_ERROR
        host_ip = query_res[0].public_ip
        return host_ip, SUCCEED

    @classmethod
    def get_args(cls) -> tuple:
        """
            get args and token from request,and get host ip and
            host token from database by them

        Returns:
            tuple: host token,host ip
        """
        data, status = BaseResponse.verify_request(schema=AgentPluginInfoSchema)
        if status != SUCCEED:
            return status, {}
        host_ip, status_code = cls.get_host_ip(data.get('host_id'))
        if status_code != SUCCEED:
            return status_code, {}

        user = UserCache.get(data.get('username'))
        if user is None:
            return TOKEN_ERROR, {}
        host_token = user.token
        res = {
            'host_ip': host_ip,
            'host_token': host_token
        }
        return SUCCEED, res

    @classmethod
    def get_data_from_agent(cls, host_ip: str, host_token: str, agent_port: int, agent_url: str) -> dict:
        """
            Get the data we want from agent

        Args:
            host_ip(str):
            host_token(str): The host token obtained when adds a user
            agent_port(int)
            agent_url(str): how to visit agent

        Returns:
            dict(str):It contains status code, Related Information or
            expected data.
        """
        headers = {'content-type': 'application/json',
                   'access_token': host_token}
        url = f"http://{host_ip}:{agent_port}{agent_url}"
        try:
            ret = requests.get(url=url, headers=headers)
        except requests.exceptions.ConnectionError:
            return StatusCode.make_response(HTTP_CONNECT_ERROR)
        if ret.status_code == SUCCEED:
            res = {'info': json.loads(ret.text)}
            return make_response((ret.status_code, res))
        return StatusCode.make_response(ret.status_code)


class AgentPluginInfo(BaseResponse):
    """
    Interface for user get agent plugin info
    """

    def get(self) -> Response:
        """
        Interface for get agent plugin info

        Args:
            host_id (str): host machine uuid
            access_token (str): token for user login

        Returns:
            Response: response body
        """
        status, data = AgentUtil.get_args()
        if status != SUCCEED:
            return jsonify(StatusCode.make_response(status))
        res = AgentUtil.get_data_from_agent(data.get('host_ip'), data.get('host_token'), ROUTE_AGENT_PLUGIN_INFO)
        return jsonify(res)
