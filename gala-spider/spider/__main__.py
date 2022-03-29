#!/usr/bin/env python3
import os
import logging
from logging.handlers import RotatingFileHandler

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


def init_logger(app, spider_config: SpiderConfig):
    log_path = spider_config.log_conf.get('log_path')
    max_bytes = spider_config.log_conf.get('max_size') * 1000 * 1000
    backup_count = spider_config.log_conf.get('backup_count')

    log_path = os.path.realpath(log_path)
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - "
                                  "%(filename)s:%(lineno)d - %(message)s")
    handler = RotatingFileHandler(filename=log_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    app.app.logger.addHandler(handler)

    log_level = spider_config.log_conf.get('log_level', '')
    numeric_level = getattr(logging, log_level.upper())
    if not isinstance(numeric_level, int):
        print("Invalid log level: %s, use default info level alternatively.", log_level)
        numeric_level = logging.INFO
    app.app.logger.setLevel(numeric_level)


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
    init_logger(app, spider_config)
    app.run(port=spider_config.spider_port, host=spider_config.spider_server)


if __name__ == '__main__':
    main()
