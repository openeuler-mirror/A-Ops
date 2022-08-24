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
from cause_inference.cause_infer import AbnormalEvent
from cause_inference.cause_infer import cause_locating
from cause_inference.cause_infer import parse_abn_evt
from cause_inference.cause_infer import normalize_abn_score
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
    infer_kafka_conf = infer_config.kafka_conf.get('inference_topic')
    kpi_consumer = KafkaConsumer(
        kpi_kafka_conf.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=kpi_kafka_conf.get('group_id'),
    )
    cause_producer = KafkaProducer(bootstrap_servers=[kafka_server])

    while True:
        logger.logger.info('Start consuming abnormal kpi event...')
        kpi_msg = next(kpi_consumer)
        data = json.loads(kpi_msg.value)
        try:
            abn_kpi = parse_abn_evt(data)
        except DataParseException as ex:
            logger.logger.error(ex)
            continue

        metric_evts = []
        recommend_metrics = data.get('Resource', {}).get('recommend_metrics', {})
        for metric_id, metric_data in recommend_metrics.items():
            metric_evt = AbnormalEvent(
                timestamp=data.get('Timestamp'),
                abnormal_metric_id=metric_id,
                abnormal_score=normalize_abn_score(metric_data.get('score')),
                metric_labels=metric_data.get('label', {})
            )
            metric_evts.append(metric_evt)

        logger.logger.debug('abnormal kpi is: {}'.format(abn_kpi))
        logger.logger.debug('abnormal metrics are: {}'.format(metric_evts))

        try:
            cause_res = cause_locating(abn_kpi, metric_evts)
        except InferenceException as ie:
            logger.logger.error(ie)
            continue

        attributes = data.get('Attributes', {})
        cause_msg = {
            'Timestamp': abn_kpi.timestamp,
            'event_id': attributes.get('event_id', ''),
            'Atrributes': {
                'event_id': attributes.get('event_id', '')
            },
            'Resource': cause_res,
            'SeverityText': 'WARN',
            'SeverityNumber': 13,
            'Body': 'A cause inferring event for an abnormal event',
        }
        logger.logger.debug(json.dumps(cause_msg, indent=2))
        try:
            cause_producer.send(infer_kafka_conf.get('topic_id'), json.dumps(cause_msg).encode())
        except KafkaTimeoutError as ex:
            logger.logger.error(ex)
            continue
        logger.logger.info('A cause inferring event has been sent to kafka.')


if __name__ == '__main__':
    main()
