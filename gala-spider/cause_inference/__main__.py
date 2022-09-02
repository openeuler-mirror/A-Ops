import json
import os
import threading
from typing import List

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from spider.util import logger
from spider.conf import init_observe_meta_config
from spider.conf.observe_meta import ObserveMetaMgt
from cause_inference.config import infer_config
from cause_inference.config import init_infer_config
from cause_inference.model import AbnormalEvent
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
    def __init__(self, observe_meta_mgt: ObserveMetaMgt, metadata_consumer):
        super().__init__()
        self.observe_meta_mgt = observe_meta_mgt
        self.metadata_consumer = metadata_consumer

    def run(self):
        for msg in self.metadata_consumer:
            data = json.loads(msg.value)
            metadata = {}
            metadata.update(data)
            self.observe_meta_mgt.add_observe_meta_from_dict(metadata)


class AbnMetricEvtMgt:
    def __init__(self, metric_consumer: KafkaConsumer, valid_duration, aging_duration):
        self.metric_consumer = metric_consumer
        self.valid_duration = valid_duration
        self.aging_duration = aging_duration
        self.all_metric_evts: List[AbnormalEvent] = []
        self.last_evt_ts = 0

    def consume_evt(self, cur_ts):
        if self.last_evt_ts > cur_ts:
            return
        logger.logger.debug('Start consuming system abnormal event')
        for msg in self.metric_consumer:
            data = json.loads(msg.value)
            try:
                abn_evt = parse_abn_evt(data)
            except DataParseException as ex:
                logger.logger.error(ex)
                continue
            if self.is_aging(abn_evt.timestamp, cur_ts):
                continue
            if not abn_evt.update_entity_id(ObserveMetaMgt()):
                logger.logger.debug("Can't identify entity id of the metric {}".format(abn_evt.abnormal_metric_id))
                continue
            self.all_metric_evts.append(abn_evt)
            self.last_evt_ts = abn_evt.timestamp
            if self.last_evt_ts > cur_ts:
                break
        logger.logger.debug('Finished to consume system abnormal event')

    def filter_valid_evts(self, cur_ts):
        res = []
        for evt in self.all_metric_evts:
            if not self.is_valid(evt.timestamp, cur_ts):
                continue
            res.append(evt)
        return res

    def clear_aging_evts(self, cur_ts):
        res = []
        for evt in self.all_metric_evts:
            if self.is_aging(evt.timestamp, cur_ts):
                continue
            res.append(evt)
        self.all_metric_evts = res

    def is_valid(self, evt_ts, cur_ts):
        return cur_ts - self.valid_duration < evt_ts <= cur_ts

    def is_aging(self, evt_ts, cur_ts):
        return evt_ts + self.aging_duration < cur_ts


def init_metadata_consumer():
    kafka_server = infer_config.kafka_conf.get('server')
    metadata_topic = infer_config.kafka_conf.get('metadata_topic')
    metadata_consumer = KafkaConsumer(
        metadata_topic.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=metadata_topic.get('group_id')
    )
    return metadata_consumer


def init_kpi_consumer():
    kafka_server = infer_config.kafka_conf.get('server')
    kpi_kafka_conf = infer_config.kafka_conf.get('abnormal_kpi_topic')
    kpi_consumer = KafkaConsumer(
        kpi_kafka_conf.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=kpi_kafka_conf.get('group_id'),
    )
    return kpi_consumer


def init_metric_consumer():
    kafka_server = infer_config.kafka_conf.get('server')
    metric_kafka_conf = infer_config.kafka_conf.get('abnormal_metric_topic')
    metric_consumer = KafkaConsumer(
        metric_kafka_conf.get('topic_id'),
        bootstrap_servers=[kafka_server],
        group_id=metric_kafka_conf.get('group_id'),
        consumer_timeout_ms=metric_kafka_conf.get('consumer_to') * 1000,
    )
    return metric_consumer


def init_cause_producer():
    kafka_server = infer_config.kafka_conf.get('server')
    cause_producer = KafkaProducer(bootstrap_servers=[kafka_server])
    return cause_producer


def init_abn_metric_evt_mgt():
    metric_consumer = init_metric_consumer()
    valid_duration = infer_config.infer_conf.get('evt_valid_duration')
    aging_duration = infer_config.infer_conf.get('evt_aging_duration')
    abn_metric_evt_mgt = AbnMetricEvtMgt(metric_consumer, valid_duration=valid_duration, aging_duration=aging_duration)
    return abn_metric_evt_mgt


def init_obsv_meta_coll_thd():
    obsv_meta_mgt = ObserveMetaMgt()
    metadata_consumer = init_metadata_consumer()
    obsv_meta_coll_thread = ObsvMetaCollThread(obsv_meta_mgt, metadata_consumer)
    obsv_meta_coll_thread.setDaemon(True)
    return obsv_meta_coll_thread


def get_recommend_metric_evts(abn_kpi_data: dict) -> List[AbnormalEvent]:
    metric_evts = []
    obsv_meta_mgt = ObserveMetaMgt()
    recommend_metrics = abn_kpi_data.get('Resource', {}).get('recommend_metrics', {})
    for metric_id, metric_data in recommend_metrics.items():
        metric_evt = AbnormalEvent(
            timestamp=abn_kpi_data.get('Timestamp'),
            abnormal_metric_id=metric_id,
            abnormal_score=normalize_abn_score(metric_data.get('score')),
            metric_labels=metric_data.get('label', {})
        )
        if not metric_evt.update_entity_id(obsv_meta_mgt):
            logger.logger.debug("Can't identify entity id of the metric {}".format(metric_evt.abnormal_metric_id))
            continue
        metric_evts.append(metric_evt)
    return metric_evts


def gen_cause_msg(abn_kpi_data: dict, cause_res: dict) -> dict:
    attributes = abn_kpi_data.get('Attributes', {})
    cause_msg = {
        'Timestamp': abn_kpi_data.get('Timestamp'),
        'event_id': attributes.get('event_id', ''),
        'Atrributes': {
            'event_id': attributes.get('event_id', '')
        },
        'Resource': cause_res,
        'SeverityText': 'WARN',
        'SeverityNumber': 13,
        'Body': 'A cause inferring event for an abnormal event',
    }
    return cause_msg


def main():
    if not init_config():
        return
    logger.logger.info('Start cause inference service...')

    obsv_meta_mgt = ObserveMetaMgt()
    kpi_consumer = init_kpi_consumer()
    infer_kafka_conf = infer_config.kafka_conf.get('inference_topic')
    cause_producer = init_cause_producer()
    abn_metric_evt_mgt = init_abn_metric_evt_mgt()

    obsv_meta_coll_thread = init_obsv_meta_coll_thd()
    obsv_meta_coll_thread.start()

    while True:
        logger.logger.info('Start consuming abnormal kpi event...')
        kpi_msg = next(kpi_consumer)
        data = json.loads(kpi_msg.value)
        try:
            abn_kpi = parse_abn_evt(data)
        except DataParseException as ex:
            logger.logger.error(ex)
            continue
        if not abn_kpi.update_entity_id(obsv_meta_mgt):
            logger.logger.warning("Can't identify entity id of the abnormal kpi {}".format(abn_kpi.abnormal_metric_id))
            continue

        metric_evts = get_recommend_metric_evts(data)

        abn_metric_evt_mgt.consume_evt(abn_kpi.timestamp)
        abn_metric_evt_mgt.clear_aging_evts(abn_kpi.timestamp)
        abn_metric_evts = abn_metric_evt_mgt.filter_valid_evts(abn_kpi.timestamp)
        metric_evts.extend(abn_metric_evts)

        logger.logger.debug('abnormal kpi is: {}'.format(abn_kpi))
        logger.logger.debug('abnormal metrics are: {}'.format(metric_evts))

        try:
            cause_res = cause_locating(abn_kpi, metric_evts)
        except InferenceException as ie:
            logger.logger.error(ie)
            continue

        cause_msg = gen_cause_msg(data, cause_res)
        logger.logger.debug(json.dumps(cause_msg, indent=2))
        try:
            cause_producer.send(infer_kafka_conf.get('topic_id'), json.dumps(cause_msg).encode())
        except KafkaTimeoutError as ex:
            logger.logger.error(ex)
            continue
        logger.logger.info('A cause inferring event has been sent to kafka.')


if __name__ == '__main__':
    main()
