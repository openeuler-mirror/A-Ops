#!/usr/bin/env python3
import os

import connexion

from spider import encoder
from spider.conf.observe_meta import ObserveMetaMgt
from spider.conf import SpiderConfig

SPIDER_CONFIG_PATH = '/etc/spider/gala-spider.yaml'


def create_app():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Topo Graph Engine Service'})

    return app


def main():
    # init spider config
    spider_conf_path = os.environ.get('SPIDER_CONFIG_PATH') or SPIDER_CONFIG_PATH
    spider_config = SpiderConfig()
    if not spider_config.load_from_yaml(spider_conf_path):
        print('Load spider config failed.')
        return
    print('Load spider config success.')

    observe_meta_mgt = ObserveMetaMgt()
    if not observe_meta_mgt.load_from_yaml(spider_config.observe_conf_path):
        print('Load observe metadata failed.')
        return
    print('Load observe metadata success.')

    app = create_app()
    app.run(port=spider_config.spider_port, host=spider_config.spider_server)


if __name__ == '__main__':
    main()
