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
import os
from io import StringIO
from flask import jsonify, Response, request
from aops_utils.restful.status import DATABASE_CONNECT_ERROR
from aops_check.database import SESSION
from aops_check.database.dao.result_dao import ResultDao
from aops_check.utils.schema.result import (
    QueryCheckResultHostSchema,
    QueryCheckResultListSchema,
    CheckResultConfirmSchema,
    QueryResultDomainCountSchema
)
from aops_utils.restful.response import BaseResponse


class QueryCheckResultHost(BaseResponse):
    """
        Interface for get check result.
        Restful API: GET
    """

    def get(self):
        """
            Get check result by alert id
        Returns:
            Response:
                {"code": int,
                "msg": "string",
                "result": {
                    "host id": {
                        "host_ip": "ip address",
                        "host_name": "string",
                        "is_root": false
                        "host_check_result":[{
                                "is_root": boolean,
                                "label": "string",
                                "metric_name": "string",
                                "time": time
                            }
                        ...
                        ]}}}
        """
        return jsonify(self.handle_request_db(QueryCheckResultHostSchema,
                                              ResultDao(),
                                              'query_result_host',
                                              SESSION))


class QueryCheckResultList(BaseResponse):
    """
        Interface for get check result list.
        Restful API: GET
    """

    def get(self):
        """
            get check result list from database
        """
        return jsonify(self.handle_request_db(QueryCheckResultListSchema,
                                              ResultDao(),
                                              'query_result_list',
                                              SESSION))


class QueryResultTotalCount(BaseResponse):
    """
        Interface for get number of alerts
        Restful API: GET
    """

    def get(self):
        """
            get number of alerts from database
        """
        return jsonify(
            self.handle_request_db(None, ResultDao(), 'query_result_total_count', SESSION))


class ConfirmCheckResult(BaseResponse):
    """
        Interface for confirm check result
        Restful API: POST
    """

    def post(self):
        """
            confirm check result, modify confirmed value to True
        """
        return jsonify(self.handle_request_db(CheckResultConfirmSchema,
                                              ResultDao(),
                                              'confirm_check_result',
                                              SESSION))


class QueryDomainResultCount(BaseResponse):
    """
        Interface for get number of domain check result
        Restful API: GET
    """

    def get(self):
        return jsonify(self.handle_request_db(QueryResultDomainCountSchema,
                                              ResultDao(),
                                              'count_domain_check_result',
                                              SESSION))


class DownloadAlertReport(BaseResponse):
    """
    Interface for download alert report
    """

    @staticmethod
    def _str_iterator(input_str, chunk_size=1024):
        string_io = StringIO(input_str)
        while True:
            chunk = string_io.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def _file_stream(self, content, alert_id):
        if not alert_id:
            alert_id = "Not-Content"
        response = Response(self._str_iterator(content))
        response.headers["Content-Type"] = "application/octet-stream"
        response.headers["Content-Disposition"] = f"application;file_name={alert_id}.txt"
        return response

    @staticmethod
    def _beautify_stream_content(hosts: dict, domain: dict) -> str:
        if not domain or not hosts.get("result"):
            return "暂无domain和host信息"

        stream_content = f"""
        Alert ID: {domain.get('alert_id')}
        Alert Name: {domain.get('alert_name')}
        Domain: {domain.get('domain')}
        Workflow ID: {domain.get('workflow_id')}
        Workflow Name: {domain.get('workflow_name')}
        Host Num: {domain.get('host_num')}
        Level: {domain.get('level')}
        Confirmed: {domain.get('confirmed')}
        """
        for host_id, host in hosts.get("result", dict()).items():
            host = f"""
            Host ID: {host_id}
            Host Name: {host['host_name']}
            Is Root: {host['is_root']}
            Host Check:

            """
            check_result = ""
            for host_check in host.get("host_check_result", list()):
                check_result += f"""
                Label: {host_check['label']}
                Metric Name: {host_check['metric_name']}
                Time: {host_check['time']}

                """ + os.linesep()
            stream_content += host + check_result
        return stream_content

    def get(self):
        """
        Get file stream
        """
        result_dao = ResultDao()
        if not result_dao.connect(SESSION):
            return jsonify(self.make_response(DATABASE_CONNECT_ERROR))

        hosts = self.handle_request(None, result_dao, 'query_result_host')
        domain_info = self.handle_request(None, result_dao, 'query_result_list')
        stream_content = self._beautify_stream_content(hosts=hosts["result"], domain=domain_info)
        return self._file_stream(content=stream_content, alert_id=request.args.get("alert_id",""))