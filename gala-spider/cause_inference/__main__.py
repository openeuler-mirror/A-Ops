import json

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from spider.util import logger
from spider.conf import init_observe_meta_config
from cause_inference import config
from cause_inference.cause_infer import cause_locating
from cause_inference.cause_infer import client_to_server_kpi
from cause_inference.cause_infer import filter_valid_evts
from cause_inference.cause_infer import clear_aging_evts
from cause_inference.cause_infer import parse_abn_evt
from cause_inference.exceptions import InferenceException
from cause_inference.exceptions import DataParseException


def init_config():
    log_conf = {
        'log_path': config.LOG_PATH,
        'log_level': config.LOG_LEVEL,
        'max_size': config.LOG_MAX_SIZE,
        'backup_count': config.LOG_BACKUP_COUNT,
    }
    logger.init_logger('cause-inference', log_conf)

    # 配置初始化
    if not init_observe_meta_config(config.OBSERVE_META_PATH):
        logger.logger.error('Load observe metadata failed.')
        return False
    logger.logger.info('Load observe metadata success.')

    return True


def main():
    if not init_config():
        return
    logger.logger.info('Start cause inference service...')

    consumer_to_ms = config.KAFKA_CONSUMER_TO * 1000
    kpi_consumer = KafkaConsumer(
        config.KAFKA_ABNORMAL_KPI_TOPIC,
        bootstrap_servers=[config.KAFKA_SERVER],
        group_id=config.KAFKA_KPI_GROUP_ID,
        auto_offset_reset=config.KAFKA_AUTO_OFFSET_RESET
    )
    metric_consumer = KafkaConsumer(
        config.KAFKA_ABNORMAL_METRIC_TOPIC,
        bootstrap_servers=[config.KAFKA_SERVER],
        group_id=config.KAFKA_METRIC_GROUP_ID,
        consumer_timeout_ms=consumer_to_ms,
        auto_offset_reset=config.KAFKA_AUTO_OFFSET_RESET
    )
    cause_producer = KafkaProducer(bootstrap_servers=[config.KAFKA_SERVER])

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
                cause_producer.send(config.KAFKA_CAUSE_INFER_TOPIC, json.dumps(cause_msg).encode())
            except KafkaTimeoutError as ex:
                logger.logger.error(ex)

        all_metric_evts = clear_aging_evts(all_metric_evts, abn_kpi.timestamp)


if __name__ == '__main__':
    main()
