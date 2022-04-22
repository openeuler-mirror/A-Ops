from typing import List

from spider.util import logger
from spider.entity_mgt import ObserveEntity
from spider.entity_mgt import Relation
from spider.entity_mgt import DirectRelationCreator
from spider.entity_mgt import IndirectRelationCreator
from spider.dao import ObserveEntityDao
from spider.dao import RelationDao
from spider.data_process import DataProcessor


class StorageService:
    def __init__(self, entity_dao: ObserveEntityDao, relation_dao: RelationDao):
        self.entity_dao: ObserveEntityDao = entity_dao
        self.relation_dao: RelationDao = relation_dao

    def store_graph(self, ts_sec, observe_entities: List[ObserveEntity], relations: List[Relation]) -> bool:
        if not self.entity_dao.add_all(ts_sec, observe_entities):
            logger.logger.error('Failed to store observe entities')
            return False
        if not self.relation_dao.add_all(ts_sec, relations):
            logger.logger.error('Failed to store relations')
            return False
        return True


class DataCollectionService:
    def __init__(self, data_processor: DataProcessor):
        self.data_processor: DataProcessor = data_processor

    def get_observe_entities(self, timestamp=None) -> List[ObserveEntity]:
        return self.data_processor.get_observe_entities(timestamp)


class CalculationService:
    def get_all_relations(self, observe_entities: List[ObserveEntity]) -> List[Relation]:
        relations: List[Relation] = []
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        relations.extend(direct_relations)
        indirect_relations = IndirectRelationCreator.create_relations(observe_entities, direct_relations)
        relations.extend(indirect_relations)

        return relations
