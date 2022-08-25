import os

import yaml

from spider.util import logger


class InferConfig:
    def __init__(self):
        self.data_agent = 'gala_gopher'

        self.infer_conf = {
            'tolerated_bias': 120,
            'topo_depth': 10,
            'root_topk': 3,
            'infer_policy': 'dfs',
            'sample_duration': 600,
            'evt_valid_duration': 120,
            'evt_aging_duration': 600,
        }

        self.log_conf = {
            'log_path': '/var/log/gala-inference/inference.log',
            'log_level': 'INFO',
            'max_size': 10,
            'backup_count': 10,
        }

        self.kafka_conf = {
            'server': '',
            'metadata_topic': {
                'topic_id': '',
                'group_id': 'metadata-inference',
            },
            'abnormal_kpi_topic': {
                'topic_id': '',
                'group_id': 'abn-kpi-inference',
            },
            'abnormal_metric_topic': {
                'topic_id': '',
                'group_id': 'abn-metric-inference',
                'consumer_to': 1,
            },
            'inference_topic': {
                'topic_id': '',
            }
        }

        self.arango_conf = {
            'url': '',
            'db_name': '',
        }

        self.prometheus_conf = {
            'base_url': '',
            'range_api': '',
            'step': 5,
        }

    def load_from_yaml(self, conf_path: str) -> bool:
        real_path = os.path.realpath(conf_path)
        try:
            with open(real_path, 'rb') as file:
                result = yaml.safe_load(file.read())
        except IOError as ex:
            logger.logger.error('Unable to load config file: {}'.format(ex))
            return False

        infer_conf = result.get('inference', {})
        kafka_conf = result.get('kafka', {})
        arango_conf = result.get('arangodb', {})
        log_conf = result.get('log', {})
        prometheus_conf = result.get('prometheus', {})

        self.infer_conf.update(infer_conf)
        self.kafka_conf.update(kafka_conf)
        self.arango_conf.update(arango_conf)
        self.log_conf.update(log_conf)
        self.prometheus_conf.update(prometheus_conf)

        return True


def init_infer_config(conf_path) -> bool:
    logger.logger.info('Start init inference config.')
    if not infer_config.load_from_yaml(conf_path):
        logger.logger.error('Init inference config failed.')
        return False
    logger.logger.info('Init inference config success.')
    return True


infer_config = InferConfig()
