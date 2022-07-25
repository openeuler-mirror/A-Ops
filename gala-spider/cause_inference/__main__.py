import json
import os
import threading

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from spider.util import logger
from spider.conf import init_observe_meta_config
from spider.conf.observe_meta import ObserveMetaMgt
from cause_inference.config import infer_config
from cause_inference.config import init_infer_config
from cause_inference.cause_infer import cause_locating
from cause_inference.cause_infer import client_to_server_kpi
from cause_inference.cause_infer import filter_valid_evts
from cause_inference.cause_infer import clear_aging_evts
from cause_inference.cause_infer import parse_abn_evt
from cause_inference.exceptions import InferenceException
from cause_inference.exceptions import DataParseException

INFER_CONFIG_PATH = '/etc/gala-inference/gala-inference.yaml'
EXT_OBSV_META_PATH = '/etc/gala-inference/ext-observe-meta.yaml'


def init_config():
    conf_path = os.environ.get('INFER_CONFIG_PATH') or INFER_CONFIG_PATH
    if not init_infer_config(conf_path):
        return False
    logger.init_logger('gala-inference', infer_config.log_conf)

    if not init_observe_meta_config(infer_config.data_agent, EXT_OBSV_META_PATH):
        logger.logger.error('Load observe metadata failed.')
        return False
    logger.logger.info('Load observe metadata success.')

    return True


class ObsvMetaCollThread(threading.Thread):
    def __init__(self, observe_meta_mgt: ObserveMetaMgt, kafka_conf: dict):
        super().__init__()
        self.observe_meta_mgt = observe_meta_mgt
        self.metadata_consumer = KafkaConsumer(
            kafka_conf.get('topic_id'),
            bootstrap_servers=[kafka_conf.get('server')],
            group_id=kafka_conf.get('group_id')
        )

    def run(self):
        for msg in self.metadata_consumer:
            data = json.loads(msg.value)
            metadata = {}
            metadata.update(data)
            self.observe_meta_mgt.add_observe_meta_from_dict(metadata)


def main():
    if not init_config():
        return
    logger.logger.info('Start cause inference service...')

    metadata_kafka_conf = {
        'server': infer_config.kafka_conf.get('server'),
        'topic_id': infer_config.kafka_conf.get('metadata_topic').get('topic_id'),
        'group_id': infer_config.kafka_conf.get('metadata_topic').get('group_id'),
    }
    obsv_meta_coll_thread = ObsvMetaCollThread(ObserveMetaMgt(), metadata_kafka_conf)
    obsv_meta_coll_thread.setDaemon(True)
    obsv_meta_coll_thread.start()

    kafka_server = infer_config.kafka_conf.get('server')
    kpi_kafka_conf = infer_config.kafka_conf.get('abnormal_kpi_topic')
    metric_kafka_conf = infer_config.kafka_conf.get('abnormal_metric_topic')
    infer_kafka_conf = infer_config.kafka_conf.get('inference_topic')
    kpi_consumer = KafkaConsumer(
        kpi_kafka_conf.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=kpi_kafka_conf.get('group_id'),
    )
    consumer_to_ms = metric_kafka_conf.get('consumer_to') * 1000
    metric_consumer = KafkaConsumer(
        metric_kafka_conf.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=metric_kafka_conf.get('group_id'),
        consumer_timeout_ms=consumer_to_ms,
    )
    cause_producer = KafkaProducer(bootstrap_servers=[kafka_server])

    all_metric_evts = []
    last_metric_ts = 0
    while True:
        logger.logger.debug('Start consuming abnormal kpi event...')
        kpi_msg = next(kpi_consumer)
        data = json.loads(kpi_msg.value)
        try:
            abn_kpi = parse_abn_evt(data)
        except DataParseException as ex:
            logger.logger.error(ex)
            continue
        try:
            mapped_abn_kpi = client_to_server_kpi(abn_kpi)
        except DataParseException as ex:
            logger.logger.error(ex)
            continue
        if last_metric_ts < abn_kpi.timestamp:
            logger.logger.debug('Start consuming abnormal metric event...')
            for metric_msg in metric_consumer:
                metric_data = json.loads(metric_msg.value)
                try:
                    abn_metric = parse_abn_evt(metric_data)
                except DataParseException as ex:
                    logger.logger.error(ex)
                    continue
                all_metric_evts.append(abn_metric)
                last_metric_ts = abn_metric.timestamp
                if abn_metric.timestamp > abn_kpi.timestamp:
                    break
        metric_evts = filter_valid_evts(all_metric_evts, abn_kpi.timestamp)
        if len(metric_evts) == 0:
            logger.logger.warning('No abnormal metric event detected.')
            continue

        logger.logger.debug('abnormal kpi is: {}'.format(abn_kpi))
        logger.logger.debug('mapped abnormal kpi is: {}'.format(mapped_abn_kpi))
        logger.logger.debug('abnormal metrics are: {}'.format(metric_evts))

        causes = []
        try:
            causes = cause_locating(mapped_abn_kpi, metric_evts, abn_kpi)
        except InferenceException as ie:
            logger.logger.error(ie)
        if len(causes) > 0:
            cause_msg = {
                'Timestamp': abn_kpi.timestamp,
                'Atrributes': {},
                'Resource': {
                    'abnormal_kpi': abn_kpi.to_dict(),
                    'cause_metrics': [cause.to_dict() for cause in causes]
                },
                'SeverityText': 'WARN',
                'SeverityNumber': 14,
                'Body': 'A cause inferring event for an abnormal event',
            }
            try:
                cause_producer.send(infer_kafka_conf.get('topic_id'), json.dumps(cause_msg).encode())
            except KafkaTimeoutError as ex:
                logger.logger.error(ex)

        all_metric_evts = clear_aging_evts(all_metric_evts, abn_kpi.timestamp)


if __name__ == '__main__':
    main()
