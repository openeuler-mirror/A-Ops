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
Description:
"""
import time
from unittest import TestCase, skipUnless, mock

from aops_database.proxy.data import KpiDataBase, LogDatabase


class TestKpiDatabase(TestCase):
    """
    Test case for getting Kpi data
    """
    # use default ip and port config in /etc/aops/database.ini
    proxy = KpiDataBase()

    # prometheus cannot manually insert data, therefore mocking the query result and
    # there is no need to connect the proxy.
    @mock.patch.object(KpiDataBase, "query")
    def test_get_kpi_data(self, mock_query):
        """
        test parsing query result from prometheus
        Args:
            mock_query: the query function of prometheus proxy

        Returns:

        """
        mock_query.side_effect = [
            [True, [
                {
                    "metric":
                        {
                            "__name__": "node_cpu_seconds_total",
                            "cpu": "0",
                            "instance": "1.1.1.1:9100",
                            "job": "node",
                            "mode": "idle"
                        },
                    "values": [[1111100005.931, "1187112.68"], [1111100006.931, "1187123.68"]]
                },
                {
                    "metric":
                        {
                            "__name__": "node_cpu_seconds_total",
                            "cpu": "0",
                            "instance": "1.1.1.1:9100",
                            "job": "node",
                            "mode": "iowait"
                        },
                    "values": [[1111100005.931, "3.68"], [1111100006.931, "2.68"]]
                }]],
            [False, [{
                "host_id": "1.1.1.1",
                "name": "node_schedstat_running_seconds_total",
                "label": {"cpu": "0"}
            }]],
            [True, [{
                "metric":
                    {
                        "__name__": "node_schedstat_running_seconds_total",
                        "cpu": "0",
                        "instance": "1.1.1.2:9100",
                        "job": "node",
                    },
                "values": [[1111100004.931, "221.68"], [1111100005.931, "225.68"]]
            }]]
        ]
        query_args = {
            "time_range": [1111100000, 1111100010],
            "data_infos": [
                {
                    "host_id": "1.1.1.1",
                    "data_list": [
                        {
                            "name": "node_cpu_seconds_total",
                            "label": {"cpu": "0"}
                        },
                        {
                            "name": "node_schedstat_running_seconds_total",
                            "label": {"cpu": "0"}
                        }]},
                {
                    "host_id": "1.1.1.2",
                    "data_list": [
                        {
                            "name": "node_schedstat_running_seconds_total",
                            "label": {"cpu": "0"}
                        }]}]}

        expected_res = (206, {"succeed_list": [
            {"host_id": "1.1.1.1", "name": "node_cpu_seconds_total",
             "label": {"cpu": "0", "mode": "idle"},
             "values": [[1111100005.931, "1187112.68"], [1111100006.931, "1187123.68"]]},
            {"host_id": "1.1.1.1", "name": "node_cpu_seconds_total",
             "label": {"cpu": "0", "mode": "iowait"},
             "values": [[1111100005.931, "3.68"], [1111100006.931, "2.68"]]},
            {"host_id": "1.1.1.2", "name": "node_schedstat_running_seconds_total",
             "label": {"cpu": "0"},
             "values": [[1111100004.931, "221.68"], [1111100005.931, "225.68"]]},
        ], "fail_list": [
            {"host_id": "1.1.1.1", "name": "node_schedstat_running_seconds_total",
             "label": {"cpu": "0"}}
        ]})
        res = self.proxy.get_data(query_args)
        self.assertEqual(expected_res, res)


class TestLogDatabase(TestCase):
    """
    Test case for getting Log data
    """
    # use default ip and port config in /etc/aops/database.ini
    proxy = LogDatabase()
    proxy.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        TestLogDatabase.proxy.close()

    def setUp(self):
        TestLogDatabase.proxy.delete_index("1.1.1.1")
        TestLogDatabase.proxy.delete_index("1.1.1.2")

    def tearDown(self):
        TestLogDatabase.proxy.delete_index("1.1.1.1")
        TestLogDatabase.proxy.delete_index("1.1.1.2")

    @skipUnless(proxy.connected, "Elasticsearch is not connected.")
    def test_get_log_data(self):
        """
        test getting and parsing log data from elasticsearch
        Returns:

        """
        # insert test data, the timestamp in elasticsearch is not unix timestamp
        data1_1 = {"@timestamp": "2000-01-01T00:00:02.000000000+08:00",
                   "data_item": "history", "message": "aaa"}
        data1_2 = {"@timestamp": "2000-01-01T00:00:01.000000000+08:00",
                   "data_item": "history", "message": "bbb"}
        data1_3 = {"@timestamp": "2000-01-01T00:00:06.000000000+08:00",
                   "data_item": "messages", "message": "ccc"}
        data2_1 = {"@timestamp": "2000-01-01T00:00:05.000000000+08:00",
                   "data_item": "history", "message": "ddd"}
        data2_2 = {"@timestamp": "2000-01-01T00:00:05.000000000+08:00",
                   "data_item": "history", "message": "eee"}

        TestLogDatabase.proxy.insert("1.1.1.1", data1_1)
        TestLogDatabase.proxy.insert("1.1.1.1", data1_2)
        TestLogDatabase.proxy.insert("1.1.1.1", data1_3)
        TestLogDatabase.proxy.insert("1.1.1.2", data2_1)
        TestLogDatabase.proxy.insert("1.1.1.2", data2_2)

        time.sleep(1)

        query_args = {
            "time_range": [946656000, 946656010],
            "data_infos": [
                {
                    "host_id": "1.1.1.1",
                    "data_list": ["messages", "history"],
                },
                {
                    "host_id": "1.1.1.2",
                    "data_list": ["history"],
                }
            ]
        }

        res = self.proxy.get_data(query_args)
        expected_res = (200, {"succeed_list": [
            {"host_id": "1.1.1.1", "name": "history", "values":
                [[946656001, "bbb"], [946656002, "aaa"]]},
            {"host_id": "1.1.1.1", "name": "messages", "values":
                [[946656006, "ccc"]]},
            {"host_id": "1.1.1.2", "name": "history", "values":
                [[946656005, "ddd"], [946656005, "eee"]]},
        ], "fail_list": []})

        self.assertEqual(expected_res, res)
