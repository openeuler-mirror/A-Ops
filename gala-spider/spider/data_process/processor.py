from typing import List
from abc import ABCMeta
from abc import abstractmethod

from spider.entity_mgt.models import ObserveEntity


class DataProcessor(metaclass=ABCMeta):
    @abstractmethod
    def get_observe_entities(self, timestamp: float = None) -> List[ObserveEntity]:
        pass
