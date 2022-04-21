import os
import time
import logging

from spider.conf import SpiderConfig
from spider.conf import init_spider_config
from spider.conf import init_observe_meta_config
from spider.util import logger
from spider.data_process import DataProcessorFactory
from spider.dao.arangodb import ArangoObserveEntityDaoImpl
from spider.dao.arangodb import ArangoRelationDaoImpl
from spider.service import StorageService
from spider.service import DataCollectionService
from spider.service import CalculationService
from spider.exceptions import StorageException

SPIDER_CONFIG_PATH = '/etc/spider/gala-spider.yaml'


def main():
    # init spider config
    spider_conf_path = os.environ.get('SPIDER_CONFIG_PATH') or SPIDER_CONFIG_PATH
    if not init_spider_config(spider_conf_path):
        return
    spider_config = SpiderConfig()

    if not init_observe_meta_config(spider_config.observe_conf_path):
        return

    logger.init_logger('spider-storage', spider_config.log_conf)

    # 初始化相关的服务
    # 初始化数据采集服务
    data_source = spider_config.db_agent
    data_processor = DataProcessorFactory.get_instance(data_source)
    if data_processor is None:
        logger.logger.error("Unknown data source:{}, please check!".format(data_source))
        return
    collect_srv = DataCollectionService(data_processor)
    # 初始化关系计算服务
    calc_srv = CalculationService()
    # 初始化存储服务
    db_conf = spider_config.storage_conf.get('db_conf')
    try:
        entity_dao = ArangoObserveEntityDaoImpl(db_conf)
        relation_dao = ArangoRelationDaoImpl(db_conf)
    except StorageException as ex:
        logger.logger.error(ex)
        return
    storage_srv = StorageService(entity_dao=entity_dao, relation_dao=relation_dao)

    # 启动存储业务逻辑
    storage_period = spider_config.storage_conf.get('period')
    while True:
        cur_ts_sec = int(time.time())
        observe_entities = collect_srv.get_observe_entities(cur_ts_sec)
        relations = calc_srv.get_all_relations(observe_entities)
        if not storage_srv.store_graph(cur_ts_sec, observe_entities, relations):
            logger.logger.error('Spider graph stores failed.')
        else:
            logger.logger.info('Spider graph stores successfully.')

        time.sleep(storage_period * 60)


if __name__ == '__main__':
    main()
