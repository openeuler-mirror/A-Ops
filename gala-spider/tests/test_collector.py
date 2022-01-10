from spider.conf import SpiderConfig
from spider.collector.data_collector import DataRecord
from spider.collector.prometheus_collector import PrometheusCollector
from .common import assert_data_record, gen_instant_resp_data, gen_task_metric_item, append_metric_items
from .common import init_spider_config


def setup_module():
    init_spider_config()


class TestPrometheusCollector:

    def setup_class(self):
        spider_config = SpiderConfig()
        self.collector = PrometheusCollector(**spider_config.prometheus_conf)
        self.metric_id = "gala_gopher_task_fork_count"
        self.resp_data = gen_instant_resp_data()
        self.metric_item = gen_task_metric_item('fork_count')
        append_metric_items(self.resp_data, [self.metric_item])

    def _mock_requests(self, requests_mock):
        spider_config = SpiderConfig()

        prometheus_conf = spider_config.prometheus_conf
        url = prometheus_conf.get("base_url") + prometheus_conf.get("instant_api")
        requests_mock.get(url, json=self.resp_data)

    def test_get_instant_data(self, requests_mock):
        self._mock_requests(requests_mock)

        resp_data = self.collector.get_instant_data(self.metric_id, 0)

        assert isinstance(resp_data, list)
        assert isinstance(resp_data[0], DataRecord)
        assert_data_record(resp_data[0], self.metric_item)
