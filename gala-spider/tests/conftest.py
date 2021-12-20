import os

import pytest

from spider.collector.prometheus_collector import PrometheusCollector
from spider.conf.observe_meta import ObserveMetaMgt
from spider.data_process.prometheus_processor import PrometheusProcessor


@pytest.fixture
def prometheus_conf():
    return {
        "base_url": "http://localhost",
        "instant_api": "/api/v1/query",
        "range_api": "/api/v1/query_range"
    }


@pytest.fixture
def observe_meta_mgt():
    cur_file_path, _ = os.path.split(os.path.abspath(__file__))
    observe_meta_mgt = ObserveMetaMgt()
    observe_meta_mgt.load_from_yaml(cur_file_path + "./static/tmp_observe.yaml")
    assert len(observe_meta_mgt.observe_meta_map) > 0
    return observe_meta_mgt


@pytest.fixture
def prometheus_collector(prometheus_conf):
    return PrometheusCollector(**prometheus_conf)


@pytest.fixture
def prometheus_processor():
    return PrometheusProcessor()
