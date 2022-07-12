import os
import time
import threading
import json

from kafka import KafkaConsumer

from spider.conf import SpiderConfig
from spider.conf import init_spider_config
from spider.conf import init_observe_meta_config
from spider.conf.observe_meta import ObserveMetaMgt
from spider.util import logger
from spider.data_process import DataProcessorFactory
from spider.dao.arangodb import ArangoObserveEntityDaoImpl
from spider.dao.arangodb import ArangoRelationDaoImpl
from spider.service import StorageService
from spider.service import DataCollectionService
from spider.service import CalculationService
from spider.exceptions import StorageException

SPIDER_CONFIG_PATH = '/etc/gala-spider/gala-spider.yaml'
TOPO_RELATION_PATH = '/etc/gala-spider/topo-relation.yaml'
EXT_OBSV_META_PATH = '/etc/gala-spider/ext-observe-meta.yaml'


class ObsvMetaCollThread(threading.Thread):
    def __init__(self, observe_meta_mgt: ObserveMetaMgt, kafka_conf: dict):
        super().__init__()
        self.observe_meta_mgt = observe_meta_mgt
        self.metadata_consumer = KafkaConsumer(
            kafka_conf.get('metadata_topic'),
            bootstrap_servers=[kafka_conf.get('server')],
            group_id=kafka_conf.get('metadata_group_id')
        )

    def run(self):
        for msg in self.metadata_consumer:
            data = json.loads(msg.value)
            metadata = {}
            metadata.update(data)
            self.observe_meta_mgt.add_observe_meta_from_dict(metadata)


def main():
    # init spider config
    spider_conf_path = os.environ.get('SPIDER_CONFIG_PATH') or SPIDER_CONFIG_PATH
    if not init_spider_config(spider_conf_path):
        return
    spider_config = SpiderConfig()
    logger.init_logger('spider-storage', spider_config.log_conf)

    if not init_observe_meta_config(TOPO_RELATION_PATH, spider_config.data_agent, EXT_OBSV_META_PATH):
        return

    obsv_meta_coll_thread = ObsvMetaCollThread(ObserveMetaMgt(), spider_config.kafka_conf)
    obsv_meta_coll_thread.setDaemon(True)
    obsv_meta_coll_thread.start()

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
        time.sleep(storage_period)

        cur_ts_sec = int(time.time())
        observe_entities = collect_srv.get_observe_entities(cur_ts_sec)
        if len(observe_entities) == 0:
            logger.logger.debug('No observe entities collected.')
            continue
        relations = calc_srv.get_all_relations(observe_entities)
        if not storage_srv.store_graph(cur_ts_sec, observe_entities, relations):
            logger.logger.error('Spider graph stores failed.')
        else:
            logger.logger.info('Spider graph stores successfully.')


if __name__ == '__main__':
    main()
