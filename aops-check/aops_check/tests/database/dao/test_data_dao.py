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
Time: 2022-07-27
Author: YangYunYi
Description: Test Data dao
"""
import unittest
from unittest.mock import Mock, MagicMock
from prometheus_api_client import PrometheusConnect, PrometheusApiClientException
from aops_utils.restful.status import SUCCEED, PARAM_ERROR, PARTIAL_SUCCEED
from aops_check.database.dao.data_dao import DataDao
from aops_check.conf import configuration

test_cases = [
    # input 1: normal
    {
        "time_range": [1658826729, 1658913129],
        "host_list": [{"host_id": "id1", "public_ip": "172.168.128.164", "instance_port": 9100}]
    },
    # input 2: no port
    {
        "time_range": [1658826729, 1658913129],
        "host_list": [{"host_id": "id1", "public_ip": "172.168.128.164"}]
    },
    # input 3: empty host list
    {
        "time_range": [1658826729, 1658913129],
        "host_list": []
    },
    # input 4: multi-host
    {
        "time_range": [1658826729, 1658913129],
        "host_list": [{"host_id": "id1", "public_ip": "172.168.128.164", "instance_port": 9100},
                      {"host_id": "id1", "public_ip": "172.168.128.164", "instance_port": 8080},
                      {"host_id": "id2", "public_ip": "172.168.128.165"}]
    }
]

metric_list_ret = [
    # metric ret1 : normal
    [{'metric': {'__name__': 'go_gc_duration_seconds', 'instance': '172.168.128.164:9100',
                 'job': 'prometheus', 'quantile': '0'},
      'value': [1658975590.796, '0.000032261']},
     {'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '503',
                 'instance': '172.168.128.164:9100', 'job': 'prometheus'},
      'value': [1658975590.796, '0']},
     {'metric': {'__name__': 'up', 'instance': '172.168.128.164:9100',
                 'job': 'prometheus'},
      'value': [1658975590.796, '1']}],

    # metric ret2 : no __name__ | no job | no value
    [{'metric': {'instance': '172.168.128.164:9100',
                 'job': 'prometheus', 'quantile': '0'},
      'value': [1658975590.796, '0.000032261']},
     {'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '503',
                 'instance': '172.168.128.164:9100'},
      'value': [1658975590.796, '0']},
     {'metric': {'__name__': 'up', 'instance': '172.168.128.164:9100',
                 'job': 'prometheus'}}],

    # metric ret3 : normal port 8080
    [{'metric': {'__name__': 'go_gc_duration_seconds1', 'instance': '172.168.128.164:8080',
                 'job': 'prometheus', 'quantile': '0'},
      'value': [1658975590.796, '0.000032261']},
     {'metric': {'__name__': 'promhttp_metric_handler_requests_total1', 'code': '503',
                 'instance': '172.168.128.164:8080', 'job': 'prometheus'},
      'value': [1658975590.796, '0']},
     {'metric': {'__name__': 'up1', 'instance': '172.168.128.164:8080',
                 'job': 'prometheus'},
      'value': [1658975590.796, '1']}],

    # metric ret4 : normal port id2 host
    [{'metric': {'__name__': 'go_gc_duration_seconds2', 'instance': '172.168.128.165:9100',
                 'job': 'prometheus', 'quantile': '0'},
      'value': [1658975590.796, '0.000032261']},
     {'metric': {'__name__': 'promhttp_metric_handler_requests_total2', 'code': '503',
                 'instance': '172.168.128.165:9100', 'job': 'prometheus'},
      'value': [1658975590.796, '0']},
     {'metric': {'__name__': 'up2', 'instance': '172.168.128.165:9100',
                 'job': 'prometheus'},
      'value': [1658975590.796, '1']}],

]

raw_data_ret = [
    # raw data 1: normal
    [[{'metric': {'__name__': 'go_gc_duration_seconds', 'instance': '172.168.128.164:9100',
                  'job': 'prometheus', 'quantile': '0'},
       'values': [[1658913069, '0.00002582'], [1658913084, '0.00002582'],
                  [1658913099, '0.00002582'], [1658913114, '0.00002738'],
                  [1658913129, '0.00002738']]}],
     [{'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '200',
                  'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '28872'], [1658913084, '28873'], [1658913099, '28874'],
                  [1658913114, '28875'], [1658913129, '28876']]}],
     [{'metric': {'__name__': 'up', 'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '1'], [1658913084, '1'], [1658913099, '1'],
                  [1658913114, '1'], [1658913129, '1']]}]],

    # raw data 2: 2 metric ret
    [[{'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '200',
                  'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '28872'], [1658913084, '28873'], [1658913099, '28874'],
                  [1658913114, '28875'], [1658913129, '28876']]}],
     [{'metric': {'__name__': 'up', 'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '1'], [1658913084, '1'], [1658913099, '1'],
                  [1658913114, '1'], [1658913129, '1']]}]],

    # raw data 3: no data | no value
    [[{'metric': {'__name__': 'go_gc_duration_seconds', 'instance': '172.168.128.164:9100',
                  'job': 'prometheus', 'quantile': '0'},
       'values': [[1658913069, '0.00002582'], [1658913084, '0.00002582'],
                  [1658913099, '0.00002582'], [1658913114, '0.00002738'],
                  [1658913129, '0.00002738']]}],
     [{'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '200',
                  'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': []}],
     []],

    # raw data 4: normal
    [[{'metric': {'__name__': 'go_gc_duration_seconds', 'instance': '172.168.128.164:9100',
                  'job': 'prometheus', 'quantile': '0'},
       'values': [[1658913069, '0.00002582'], [1658913084, '0.00002582'],
                  [1658913099, '0.00002582'], [1658913114, '0.00002738'],
                  [1658913129, '0.00002738']]}],
     [{'metric': {'__name__': 'promhttp_metric_handler_requests_total', 'code': '200',
                  'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '28872'], [1658913084, '28873'], [1658913099, '28874'],
                  [1658913114, '28875'], [1658913129, '28876']]}],
     [{'metric': {'__name__': 'up', 'instance': '172.168.128.164:9100', 'job': 'prometheus'},
       'values': [[1658913069, '1'], [1658913084, '1'], [1658913099, '1'],
                  [1658913114, '1'], [1658913129, '1']]}],
     [{'metric': {'__name__': 'go_gc_duration_seconds1', 'instance': '172.168.128.164:8080',
                  'job': 'prometheus', 'quantile': '0'},
       'values': [[1658913069, '0.00002582'], [1658913084, '0.00002582'],
                  [1658913099, '0.00002582'], [1658913114, '0.00002738'],
                  [1658913129, '0.00002738']]}],
     [{'metric': {'__name__': 'promhttp_metric_handler_requests_total1', 'code': '200',
                  'instance': '172.168.128.164:8080', 'job': 'prometheus'},
       'values': []}],
     [],
     [{'metric': {'__name__': 'go_gc_duration_seconds2', 'instance': '172.168.128.165:9100',
                  'job': 'prometheus', 'quantile': '0'},
       'values': [[1658913069, '0.00002582'], [1658913084, '0.00002582'],
                  [1658913099, '0.00002582'], [1658913114, '0.00002738'],
                  [1658913129, '0.00002738']]}],
     [{'metric': {'__name__': 'promhttp_metric_handler_requests_total5', 'code': '200',
                  'instance': '172.168.128.165:9100', 'job': 'prometheus'},
       'values': []}],
     []
     ],

]

query_ret = [
    # ret 1: normal
    {'id1': {
        'go_gc_duration_seconds'
        '{instance="172.168.128.164:9100",quantile="0"}': [[1658913069, '0.00002582'],
                                                           [1658913084, '0.00002582'],
                                                           [1658913099, '0.00002582'],
                                                           [1658913114, '0.00002738'],
                                                           [1658913129, '0.00002738']],
        'promhttp_metric_handler_requests_total'
        '{code="503",instance="172.168.128.164:9100"}': [[1658913069, '28872'],
                                                         [1658913084, '28873'],
                                                         [1658913099, '28874'],
                                                         [1658913114, '28875'],
                                                         [1658913129, '28876']],
        'up{instance="172.168.128.164:9100"}': [[1658913069, '1'], [1658913084, '1'],
                                                [1658913099, '1'], [1658913114, '1'],
                                                [1658913129, '1']]}},

    # ret 2: 2 metric ret
    {'id1': {
        'promhttp_metric_handler_requests_total'
        '{code="503",instance="172.168.128.164:9100"}': [[1658913069, '28872'],
                                                         [1658913084, '28873'],
                                                         [1658913099, '28874'],
                                                         [1658913114, '28875'],
                                                         [1658913129, '28876']],
        'up{instance="172.168.128.164:9100"}': [[1658913069, '1'], [1658913084, '1'],
                                                [1658913099, '1'], [1658913114, '1'],
                                                [1658913129, '1']]}},

    # ret 3: no value in ret | no data
    {'id1': {
        'go_gc_duration_seconds'
        '{instance="172.168.128.164:9100",quantile="0"}': [[1658913069, '0.00002582'],
                                                           [1658913084, '0.00002582'],
                                                           [1658913099, '0.00002582'],
                                                           [1658913114, '0.00002738'],
                                                           [1658913129, '0.00002738']],
        'promhttp_metric_handler_requests_total{code="503",instance="172.168.128.164:9100"}': [],
        'up{instance="172.168.128.164:9100"}': None}},

    # ret 4: multi-host
    {
        'id1': {
            'go_gc_duration_seconds'
            '{instance="172.168.128.164:9100",quantile="0"}': [[1658913069, '0.00002582'],
                                                               [1658913084, '0.00002582'],
                                                               [1658913099, '0.00002582'],
                                                               [1658913114, '0.00002738'],
                                                               [1658913129, '0.00002738']],
            'promhttp_metric_handler_requests_total'
            '{code="503",instance="172.168.128.164:9100"}': [[1658913069, '28872'],
                                                             [1658913084, '28873'],
                                                             [1658913099, '28874'],
                                                             [1658913114, '28875'],
                                                             [1658913129, '28876']],
            'up{instance="172.168.128.164:9100"}': [[1658913069, '1'], [1658913084, '1'],
                                                    [1658913099, '1'], [1658913114, '1'],
                                                    [1658913129, '1']],
            'go_gc_duration_seconds1'
            '{instance="172.168.128.164:8080",quantile="0"}': [[1658913069, '0.00002582'],
                                                               [1658913084, '0.00002582'],
                                                               [1658913099, '0.00002582'],
                                                               [1658913114, '0.00002738'],
                                                               [1658913129, '0.00002738']],
            'promhttp_metric_handler_requests_total1{code="503",instance="172.168.128.164:8080"}': [],
            'up1{instance="172.168.128.164:8080"}': None
        },
        'id2': {
            'go_gc_duration_seconds2'
            '{instance="172.168.128.165:9100",quantile="0"}': [[1658913069, '0.00002582'],
                                                               [1658913084, '0.00002582'],
                                                               [1658913099, '0.00002582'],
                                                               [1658913114, '0.00002738'],
                                                               [1658913129, '0.00002738']],
            'promhttp_metric_handler_requests_total2{code="503",instance="172.168.128.165:9100"}': [],
            'up2{instance="172.168.128.165:9100"}': None
        }
    }
]


class DataDaoTestcase(unittest.TestCase):
    def setUp(self) -> None:
        host = "127.0.0.1"
        port = 9200
        self.dao = DataDao(configuration, host, port)
        url = f"http://{host}:{port}"
        self.dao._prom = PrometheusConnect(url=url, disable_ssl=True)
        self.dao.connected = True

    def tearDown(self) -> None:
        self.dao.close()

    def test_query_data_should_return_succeed_when_input_is_normal(self):
        self.dao._prom.custom_query = MagicMock(return_value=metric_list_ret[0])
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[0])

        ret, data_list = self.dao.query_data(test_cases[0]["time_range"],
                                             test_cases[0]["host_list"])
        self.assertEqual(SUCCEED, ret)
        self.assertDictEqual(data_list, query_ret[0])

    def test_query_data_should_return_succeed_when_host_without_port(self):
        self.dao._prom.custom_query = MagicMock(return_value=metric_list_ret[0])
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[0])

        ret, data_list = self.dao.query_data(test_cases[1]["time_range"],
                                             test_cases[1]["host_list"])
        self.assertEqual(SUCCEED, ret)
        self.assertDictEqual(data_list, query_ret[0])

    def test_query_data_should_return_error_when_host_list_empty(self):
        ret, data_list = self.dao.query_data(test_cases[2]["time_range"],
                                             test_cases[2]["host_list"])
        self.assertEqual(PARAM_ERROR, ret)
        self.assertDictEqual(data_list, {})

    def test_query_data_should_return_None_when_no_metric_get(self):
        self.dao._prom.custom_query = MagicMock(return_value=[])
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[0])

        ret, data_list = self.dao.query_data(test_cases[1]["time_range"],
                                             test_cases[1]["host_list"])
        self.assertEqual(PARTIAL_SUCCEED, ret)
        self.assertDictEqual(data_list, {'id1': None})

    def test_query_data_should_return_None_when_metric_list_failed(self):
        self.dao._prom.custom_query = MagicMock(return_value=None)

        ret, data_list = self.dao.query_data(test_cases[0]["time_range"],
                                             test_cases[0]["host_list"])
        self.assertEqual(PARTIAL_SUCCEED, ret)
        self.assertDictEqual(data_list, {'id1': None})

    def test_query_data_should_return_None_when_metric_list_invalid(self):
        self.dao._prom.custom_query = MagicMock(return_value=metric_list_ret[1])
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[1])

        ret, data_list = self.dao.query_data(test_cases[0]["time_range"],
                                             test_cases[0]["host_list"])
        self.assertEqual(SUCCEED, ret)
        self.assertDictEqual(data_list, query_ret[1])

    def test_query_data_should_raise_when_metric_list_exception(self):
        self.dao._prom.custom_query = MagicMock(return_value=PrometheusApiClientException)
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[0])

        self.dao.query_data(test_cases[0]["time_range"], test_cases[0]["host_list"])
        self.assertRaises(PrometheusApiClientException)

    def test_query_data_should_raise_when_raw_data_exception(self):
        self.dao._prom.custom_query = MagicMock(return_value=metric_list_ret[0])
        self.dao._prom.custom_query_range = MagicMock(side_effect=PrometheusApiClientException)

        self.dao.query_data(test_cases[0]["time_range"], test_cases[0]["host_list"])
        self.assertRaises(PrometheusApiClientException)

    def test_query_data_should_return_id_key_when_mutihost(self):
        self.dao._prom.custom_query = MagicMock(side_effect=[metric_list_ret[0],
                                                             metric_list_ret[2],
                                                             metric_list_ret[3]])
        self.dao._prom.custom_query_range = MagicMock(side_effect=raw_data_ret[3])

        ret, data_list = self.dao.query_data(test_cases[3]["time_range"],
                                             test_cases[3]["host_list"])
        self.assertEqual(PARTIAL_SUCCEED, ret)
        self.assertDictEqual(data_list, query_ret[3])


if __name__ == '__main__':
    unittest.main()
