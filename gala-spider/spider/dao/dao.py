from abc import ABCMeta
from abc import abstractmethod
from typing import List

from spider.entity_mgt import ObserveEntity
from spider.entity_mgt import Relation


class BaseDao(metaclass=ABCMeta):
    @abstractmethod
    def init_connection(self):
        pass


class ObserveEntityDao(metaclass=ABCMeta):
    @abstractmethod
    def add_all(self, ts_sec, observe_entities: List[ObserveEntity]):
        pass


class RelationDao(metaclass=ABCMeta):
    @abstractmethod
    def add_all(self, ts_sec, relations: List[Relation]):
        pass
