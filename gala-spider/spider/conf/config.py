import os

import yaml

from spider.util.singleton import Singleton


class SpiderConfig(metaclass=Singleton):
    def __init__(self):
        print('config init')
        super().__init__()
        self.db_agent = None
        self.observe_conf_path = None

        self.spider_server = None
        self.spider_port = None

        self.kafka_conf = {
            'topic': None,
            'broker': None,
            'group_id': None,
        }

        self.prometheus_conf = {
            'base_url': None,
            'instant_api': None,
            'range_api': None,
            'step': 1,
        }

        self.anomaly_detection_conf = {}

    def load_from_yaml(self, conf_path: str) -> bool:
        try:
            real_path = os.path.realpath(conf_path)
            with open(real_path, 'rb') as file:
                result = yaml.safe_load(file.read())
        except IOError as ex:
            print('Unable to load config file: {}'.format(ex))
            return False

        global_conf = result.get('global', {})
        self.db_agent = global_conf.get('data_source')
        self.observe_conf_path = global_conf.get('observe_conf_path')

        spider_conf = result.get('spider', {})
        self.spider_server = spider_conf.get('server')
        self.spider_port = spider_conf.get('port')

        self.kafka_conf.update(result.get('kafka', {}))
        self.prometheus_conf.update(result.get('prometheus', {}))
        self.anomaly_detection_conf.update(result.get('anomaly_detection', {}))

        return True


if __name__ == '__main__':
    config = SpiderConfig()
    config.load_from_yaml('../../config/gala-spider.yaml')
    print(config.__dict__)
