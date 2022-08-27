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
from typing import Optional, Tuple
import requests
from flask import jsonify, json, Response, request

from aops_manager.account_manager.cache import UserCache
from aops_manager.database import SESSION
from aops_manager.database.proxy.host import HostProxy
from aops_manager.function.verify.agent import (
    AgentPluginInfoSchema,
    GetHostSceneSchema,
    SetAgentPluginStatusSchema,
    SetAgentMetricStatusSchema,
)
from aops_manager.conf.constant import (
    ROUTE_AGENT_PLUGIN_INFO,
    AGENT_PLUGIN_START,
    AGENT_PLUGIN_STOP,
    AGENT_APPLICATION_INFO,
    AGENT_COLLECT_ITEMS_CHANGE,
    CHECK_IDENTIFY_SCENE
)
from aops_manager.conf import configuration
from aops_utils.database.helper import operate, judge_return_code
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
    SET_AGENT_PLUGIN_STATUS_FAILED,
    SERVER_ERROR,
    UNKNOWN_ERROR,
    StatusCode
)


class AgentUtil:
    """
    Agent utils method
    """

    @classmethod
    def get_host_ip_with_port(cls, host_id: str) -> tuple:
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
                LOGGER.error("no such host_id %s, please check.", host_id)
                return '', NO_DATA
            proxy.close()
        else:
            LOGGER.error("connect to database error when get host ip with port of %s", host_id)
            return '', DATABASE_CONNECT_ERROR
        host_ip_with_port = f'{query_res[0].public_ip}:{query_res[0].agent_port}'
        return host_ip_with_port, SUCCEED

    @classmethod
    def get_args(cls, data) -> tuple:
        """
            get args and token from request,and get host ip and
            host token from database by them

        Returns:
            tuple: host token,host ip
        """
        host_ip_with_port, status_code = cls.get_host_ip_with_port(data.get('host_id'))
        if status_code != SUCCEED:
            return status_code, {}

        user = UserCache.get(data.get('username'))
        if user is None:
            return TOKEN_ERROR, {}
        host_token = user.token
        res = {
            'host_ip_with_port': host_ip_with_port,
            'host_token': host_token
        }
        return SUCCEED, res

    @classmethod
    def get_data_from_agent(cls, host_ip_with_port: str, host_token: str, agent_url: str) -> dict:
        """
            Get the data we want from agent

        Args:
            host_token(str): The host token obtained when adds a user
            agent_url(str): how to visit agent

        Returns:
            dict(str):It contains status code, Related Information or
            expected data.
        """
        headers = {'content-type': 'application/json',
                   'access_token': host_token}
        url = f"http://{host_ip_with_port}{agent_url}"
        try:
            ret = requests.get(url=url, headers=headers)
        except requests.exceptions.ConnectionError:
            return StatusCode.make_response(HTTP_CONNECT_ERROR)
        if ret.status_code == SUCCEED:
            res = {'info': json.loads(ret.text)}
            return make_response((ret.status_code, res))
        return StatusCode.make_response(ret.status_code)

    @classmethod
    def make_agent_url(cls, host_ip_port: str, agent_url: str):
        """
            get url of agent

        Args:
            host_ip_port(str): agent public ip
            agent_url(str): how to visit agent

        Returns:
            url(str): url of agent
        """
        url = f"http://{host_ip_port}{agent_url}"
        return url

    @classmethod
    def make_agent_request(cls, agent_url: str, method: str,
                           header: Optional[dict] = None,
                           params: Optional[dict] = None,
                           data: Optional[dict] = None) -> Tuple[int, dict]:
        """
            Send request to agent

        Args:
            agent_url(str): how to visit agent
            method(str) :  method of request
            header(dict): header of request
            params(dict): param of request
            data(data): data of request

        Returns:
            status_code(int): status code of response
            dict(str): It contains status code, Related Information or
            expected data.
        """
        headers = {'content-type': 'application/json'}
        if header:
            headers.update(header)
        try:
            if method == "get":
                ret = requests.get(url=agent_url, headers=headers, params=params)
            elif method == "post":
                ret = requests.post(url=agent_url, headers=headers,
                                    params=params, data=json.dumps(data))
            else:
                LOGGER.error("Unsupported method %s send to agent url%s.", method, agent_url)
                return SERVER_ERROR, {}
            if ret.status_code == SUCCEED:
                res = json.loads(ret.text)
                return res.get("code", UNKNOWN_ERROR), res
            return ret.status_code, {}
        except requests.exceptions.ConnectionError:
            return HTTP_CONNECT_ERROR, {}


class AgentPluginInfo(BaseResponse):
    """
    Interface for user get agent plugin info
    """

    @staticmethod
    def _handle(args):
        """
        Handle function

        Args:
            args (dict): request parameter

        Returns:
            tuple: (status code, result)
        """
        status, data = AgentUtil.get_args(args)
        if status != SUCCEED:
            LOGGER.error("Get Agent data failed.")
            return status, {}
        agent_header = {'access_token': data.get('host_token')}
        status, ret = AgentUtil.make_agent_request(AgentUtil.make_agent_url(data.get('host_ip_with_port'),
                                                                            ROUTE_AGENT_PLUGIN_INFO),
                                                   "get", header=agent_header)

        ret["info"] = ret.pop("resp", [])
        return status, ret

    def get(self) -> Response:
        """
        Interface for get agent plugin info

        Returns:
            Response: response body
        """
        return jsonify(self.handle_request(AgentPluginInfoSchema, self))


class GetHostScene(BaseResponse):
    """
    Interface for get host scene.
    Restful API: get
    """

    @staticmethod
    def __get_check_url(route: str) -> Tuple[str, dict]:
        """
        Get url of check restful

        Args:
            route(str): route of restful

        Returns:
            tuple: (url, header)
        """
        check_ip = configuration.aops_check.get("IP")
        check_port = configuration.aops_check.get("PORT")
        check_url = f"http://{check_ip}:{check_port}{route}"
        check_header = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        return check_url, check_header

    @staticmethod
    def __get_scene_data_from_agent(host_ip_port: str,
                                    header: dict) -> Tuple[int, dict]:
        """
        Get applications and collect items required for scene identification
        form agent

        Args:
            host_ip_port(str): agent restful ip and port
            header(dict): header of request

        Returns:
            tuple: (status code, result)
        """

        host_scene_info = {"applications": [], "collect_items": {}}

        # Get applications form agent
        status, data = AgentUtil.make_agent_request(AgentUtil.make_agent_url(host_ip_port,
                                                                             AGENT_APPLICATION_INFO),
                                                    "get", header)
        if status != SUCCEED:
            LOGGER.error("Get agent application of host %s failed.", host_ip_port)
            return status, host_scene_info
        host_scene_info["applications"] = data.get("resp", {}).get("running", [])

        # Get collect items form agent
        status, data = AgentUtil.make_agent_request(AgentUtil.make_agent_url(host_ip_port,
                                                                             ROUTE_AGENT_PLUGIN_INFO),
                                                    "get", header)
        if status != SUCCEED:
            LOGGER.error("Get agent collect items of host %s failed.", host_ip_port)
            return status, host_scene_info
        plugin_datas = data.get("resp", [])
        for plugin_data in plugin_datas:
            plugin_name = plugin_data.get("plugin_name")
            host_scene_info["collect_items"][plugin_name] = plugin_data.get("collect_items")

        return SUCCEED, host_scene_info

    def _handle(self, args):
        """
        Handle function

        Args:
            args (dict): request parameter

        Returns:
            tuple: (status code, result)
        """
        access_token = request.headers.get("access_token")
        status, data = AgentUtil.get_args(args)
        if status != SUCCEED:
            LOGGER.error("Get Agent data failed.")
            return status, {}
        host_ip_port = data.get('host_ip_with_port')
        host_id = args.get("host_id")

        # get application info and collect items from agent
        agent_header = {'access_token': data.get('host_token')}
        status, host_scene_info = GetHostScene.__get_scene_data_from_agent(host_ip_port,
                                                                           agent_header)
        if status != SUCCEED:
            return status, {}

        # get scene and recommend collect items from check
        check_url_get_scene, check_header = GetHostScene.__get_check_url(CHECK_IDENTIFY_SCENE)
        check_header['access_token'] = access_token
        response = self.get_response("post", check_url_get_scene, host_scene_info, check_header)
        status_code = response.get("code")
        if status_code != SUCCEED:
            LOGGER.error("Get scene of host %s from check failed.", host_id)
            return status_code, {}
        scene_ret = response.get("scene_name")

        # save scene to database
        save_args = {"host_id": host_id, "scene": scene_ret}
        status_code = operate(HostProxy(), save_args, 'save_scene', SESSION)
        if status_code != SUCCEED:
            LOGGER.error("save scene of host %s failed.", host_id)
            return status_code, {}

        return status_code, {"scene": scene_ret,
                             "collect_items": response.get("collect_items")}

    def get(self) -> Response:
        """
        Get host scene

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(GetHostSceneSchema, self, need_token=True))


class SetAgentPluginStatus(BaseResponse):
    """
    Interface for get host scene.
    Restful API: POST
    """
    status_url_map = {
        "active": AGENT_PLUGIN_START,
        "inactive": AGENT_PLUGIN_STOP
    }

    @staticmethod
    def _handle(args: dict) -> Tuple[int, dict]:
        """
        Handle function of set plugin status

        Args:
            args (dict): request parameter

        Returns:
            tuple: (status code, result)
        """
        ret = {"failed_list": [], "succeed_list": []}
        status, data = AgentUtil.get_args(args)
        if status != SUCCEED:
            LOGGER.error("Get Agent data failed.")
            return status, ret
        host_ip_port = data.get('host_ip_with_port')
        host_token = data.get('host_token')
        header = {'access_token': host_token}

        plugin_status_list = args.get('plugins')
        for plugin_name, plugin_status in plugin_status_list.items():
            if plugin_status not in SetAgentPluginStatus.status_url_map:
                LOGGER.error("Unknown plugin status of host %s plugin %s.",
                             host_ip_port, plugin_name)
                ret["failed_list"].append(plugin_name)
                continue

            operate_url = SetAgentPluginStatus.status_url_map[plugin_status]
            params = {"plugin_name": plugin_name}
            operate_status = AgentUtil.make_agent_request(AgentUtil.make_agent_url(host_ip_port,
                                                                                   operate_url), "post",
                                                          header, params)[0]
            if operate_status != SUCCEED:
                ret["failed_list"].append(plugin_name)
            else:
                ret["succeed_list"].append(plugin_name)

        return judge_return_code(ret, SET_AGENT_PLUGIN_STATUS_FAILED), ret

    def post(self) -> Response:
        """
        Get host scene

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(SetAgentPluginStatusSchema, self))


class SetAgentMetricStatus(BaseResponse):
    """
    Interface for get host scene.
    Restful API: POST
    """

    @staticmethod
    def _handle(args):
        """
        Handle function

        Args:
            args (dict): request parameter

        Returns:
            tuple: (status code, result)
        """
        status, data = AgentUtil.get_args(args)
        if status != SUCCEED:
            LOGGER.error("Get Agent data failed.")
            return status
        host_ip_port = data.get('host_ip_with_port')
        host_token = data.get('host_token')
        header = {'access_token': host_token}
        body = args.get("plugins")

        operate_response = AgentUtil.make_agent_request(
            AgentUtil.make_agent_url(host_ip_port,
                                     AGENT_COLLECT_ITEMS_CHANGE),
            "post", header, data=body)
        return operate_response

    def post(self) -> Response:
        """
        Set agent metric status

        Returns:
            dict: response body
        """
        return jsonify(self.handle_request(SetAgentMetricStatusSchema, self))
