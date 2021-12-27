import pytest
import requests

from spider.collector.data_collector import DataRecord, Label
from spider.conf.observe_meta import ObserveMetaMgt, g_observe_meta_mgt, EntityType
from spider.collector.prometheus_collector import g_prometheus_collector
from spider.data_process.prometheus_processor import PrometheusProcessor
from common import assert_data_record, assert_observe_entity
from common import gen_instant_resp_data, gen_task_metric_item, gen_tcp_link_metric_item, append_metric_items
from spider.entity_mgt import ObserveEntity, ObserveEntityCreator


class TestPrometheusProcessor:

    def setup_class(self):
        self.prometheus_processor = PrometheusProcessor()

        # test data
        self.metric_id1 = "gala_gopher_tcp_link_rx_bytes"
        self.resp_data1 = gen_instant_resp_data()
        self.metric_item11 = gen_tcp_link_metric_item('rx_bytes', machine_id='machine1')
        self.metric_item12 = gen_tcp_link_metric_item('rx_bytes', machine_id='machine2')
        append_metric_items(self.resp_data1, [self.metric_item11, self.metric_item12])

        self.metric_id2 = "gala_gopher_tcp_link_tx_bytes"
        self.resp_data2 = gen_instant_resp_data()
        self.metric_item21 = gen_tcp_link_metric_item('tx_bytes', machine_id='machine1')
        self.metric_item22 = gen_tcp_link_metric_item('tx_bytes', machine_id='machine2')
        append_metric_items(self.resp_data2, [self.metric_item21, self.metric_item22])

        self.metric_id3 = "gala_gopher_task_fork_count"
        self.resp_data3 = gen_instant_resp_data()
        self.metric_item31 = gen_task_metric_item('fork_count', pid=1)
        self.metric_item32 = gen_task_metric_item('fork_count', pid=2)
        append_metric_items(self.resp_data3, [self.metric_item31, self.metric_item32])

    def _mock_context(self, mocker, prometheus_conf, observe_meta_mgt):
        # mock prometheus collector config
        mocker.patch.object(g_prometheus_collector, 'base_url', prometheus_conf.get('base_url'))
        mocker.patch.object(g_prometheus_collector, 'instant_api', prometheus_conf.get('instant_api'))
        mocker.patch.object(g_prometheus_collector, 'range_api', prometheus_conf.get('range_api'))

        # mock observe_meta_mgt field
        mocker.patch.object(g_observe_meta_mgt, 'data_agent', observe_meta_mgt.data_agent)
        mocker.patch.object(g_observe_meta_mgt, 'observe_meta_map', observe_meta_mgt.observe_meta_map)

    def _mock_requests(self, requests_mock, prometheus_conf):
        url = prometheus_conf.get("base_url") + prometheus_conf.get("instant_api")
        requests_mock.get(url, json={})
        requests_mock.get(url + "?query={}".format(self.metric_id1), json=self.resp_data1)
        requests_mock.get(url + "?query={}".format(self.metric_id2), json=self.resp_data2)
        requests_mock.get(url + "?query={}".format(self.metric_id3), json=self.resp_data3)

    def test_collect_observe_entity(self, mocker, requests_mock, prometheus_conf,
                                    observe_meta_mgt: ObserveMetaMgt):
        self._mock_context(mocker, prometheus_conf, observe_meta_mgt)
        self._mock_requests(requests_mock, prometheus_conf)

        observe_meta = observe_meta_mgt.observe_meta_map.get(EntityType.TCP_LINK.value)
        res = self.prometheus_processor.collect_observe_entity(observe_meta, 0)

        assert isinstance(res, list)
        expect_res = [self.metric_item11, self.metric_item12, self.metric_item21, self.metric_item22]
        assert len(res) == len(expect_res)
        for ret_item, expect_item in zip(res, expect_res):
            assert isinstance(ret_item, DataRecord)
            assert_data_record(ret_item, expect_item)

    def test_collect_observe_entities(self, mocker, requests_mock, prometheus_conf,
                                      observe_meta_mgt: ObserveMetaMgt):
        self._mock_context(mocker, prometheus_conf, observe_meta_mgt)
        self._mock_requests(requests_mock, prometheus_conf)

        res = self.prometheus_processor.collect_observe_entities(0)
        assert isinstance(res, dict)
        assert len(res) == 2
        assert EntityType.TASK.value in res
        assert EntityType.TCP_LINK.value in res
        assert len(res[EntityType.TASK.value]) == 2
        assert len(res[EntityType.TCP_LINK.value]) == 4

    def test_aggregate_entities_by_label(self, mocker, requests_mock, prometheus_conf,
                                         observe_meta_mgt: ObserveMetaMgt):
        self._mock_context(mocker, prometheus_conf, observe_meta_mgt)
        self._mock_requests(requests_mock, prometheus_conf)

        observe_entities = self.prometheus_processor.collect_observe_entities(0)
        expect_res = {
            "task": [
                {"__name__": "gala_gopher_task_fork_count", "pid": 1, "fork_count": 1, "timestamp": 0,
                 "task_name": "task0", "machine_id": "machine0"},
                {"__name__": "gala_gopher_task_fork_count", "pid": 2, "fork_count": 1, "timestamp": 0,
                 "task_name": "task0", "machine_id": "machine0"},
            ]
        }
        res = self.prometheus_processor.aggregate_entities_by_label(observe_entities)
        assert isinstance(res, dict)
        assert "task" in res
        assert len(res["task"]) == len(expect_res["task"])
        for ret_item, expect_item in zip(res["task"], expect_res["task"]):
            for key in ret_item:
                assert ret_item[key] == expect_item[key]

    def test_get_observe_entities(self, mocker, requests_mock, prometheus_conf,
                                  observe_meta_mgt: ObserveMetaMgt):
        self._mock_context(mocker, prometheus_conf, observe_meta_mgt)
        self._mock_requests(requests_mock, prometheus_conf)

        task_meta = observe_meta_mgt.get_observe_meta('task')
        task_data = {'machine_id': 'machine0', 'pid': 1, 'fork_count': 1, 'task_name': 'task0', 'timestamp': 0}
        task_data1 = {'machine_id': 'machine0', 'pid': 2, 'fork_count': 1, 'task_name': 'task0', 'timestamp': 0}
        expect_res = [
            ObserveEntityCreator.create_observe_entity('task', task_data, task_meta),
            ObserveEntityCreator.create_observe_entity('task', task_data1, task_meta),
        ]
        res = self.prometheus_processor.get_observe_entities(0)
        for expect_entity in expect_res:
            is_exist = False
            for ret_entity in res:
                if ret_entity.id == expect_entity.id:
                    assert_observe_entity(ret_entity, expect_entity)
                    is_exist = True
                    break
            assert is_exist
