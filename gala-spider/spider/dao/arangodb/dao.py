from typing import List

from pyArango.collection import Collection
from pyArango.connection import Connection
from pyArango.database import Database
from pyArango.document import Document
from pyArango.theExceptions import UpdateError

from spider.util import logger
from spider.util.entity import escape_entity_id
from spider.dao import BaseDao
from spider.dao import ObserveEntityDao
from spider.dao import RelationDao
from spider.entity_mgt import ObserveEntity
from spider.entity_mgt import Relation
from spider.exceptions import StorageConnectionException

_TIMESTAMP_COLL_NAME = 'Timestamps'
_OBSERVE_ENTITY_COLL_PREFIX = 'ObserveEntities'


def _get_collection_name(collection_type, ts_sec):
    return '{}_{}'.format(collection_type, ts_sec)


def _get_doc_id(collection_name, doc_key):
    return '{}/{}'.format(collection_name, doc_key)


# arangodb 对文档的 _key 有命名约束，需要对 key 中出现的特殊字符进行替换
def _transfer_doc_key(key: str):
    return escape_entity_id(key)


def transfer_observe_entity_to_document_dict(observe_entity: ObserveEntity) -> dict:
    doc_dict = {
        '_key': _transfer_doc_key(observe_entity.id),
        'type': observe_entity.type,
        'level': observe_entity.level,
        'timestamp': observe_entity.timestamp,
    }
    doc_dict.update(observe_entity.attrs)
    return doc_dict


def transfer_relation_to_edge_dict(relation: Relation, ts_sec) -> dict:
    edge_dict = {
        'type': relation.type,
        'timestamp': ts_sec,
        'layer': relation.layer,
        '_from': _get_doc_id(_get_collection_name(_OBSERVE_ENTITY_COLL_PREFIX, ts_sec),
                             _transfer_doc_key(relation.sub_entity.id)),
        '_to': _get_doc_id(_get_collection_name(_OBSERVE_ENTITY_COLL_PREFIX, ts_sec),
                           _transfer_doc_key(relation.obj_entity.id)),
    }
    return edge_dict


class ArangoBaseDaoImpl(BaseDao):
    def __init__(self, db_conf):
        self.url = db_conf.get('url')
        self.db_name = db_conf.get('db_name')
        self.conn: Connection = None
        self.db: Database = None
        self.init_connection()

    def init_connection(self):
        if self.conn is None:
            try:
                self.conn = Connection(arangoURL=self.url)
            except Exception as ex:
                raise StorageConnectionException(ex)
        if not self.conn.hasDatabase(self.db_name):
            self.conn.createDatabase(self.db_name)
        self.db = self.conn.databases[self.db_name]

    def _add_timestamp(self, ts_sec) -> bool:
        if not self.db.hasCollection(_TIMESTAMP_COLL_NAME):
            self.db.createCollection(name=_TIMESTAMP_COLL_NAME)
        coll: Collection = self.db.collections[_TIMESTAMP_COLL_NAME]
        ts_doc: Document = coll.createDocument({'_key': str(ts_sec)})
        try:
            ts_doc.save(overwrite=True)
        except UpdateError as ex:
            logger.logger.error(ex)
            return False
        return True


class ArangoObserveEntityDaoImpl(ArangoBaseDaoImpl, ObserveEntityDao):
    def __init__(self, db_conf):
        ArangoBaseDaoImpl.__init__(self, db_conf)

    def add_all(self, ts_sec, observe_entities: List[ObserveEntity]) -> bool:
        if not observe_entities:
            return True

        if not self._add_timestamp(ts_sec):
            return False

        docs = []
        for observe_entity in observe_entities:
            docs.append(transfer_observe_entity_to_document_dict(observe_entity))

        coll_name = _get_collection_name(_OBSERVE_ENTITY_COLL_PREFIX, ts_sec)
        if not self.db.hasCollection(coll_name):
            self.db.createCollection(name=coll_name)
        coll: Collection = self.db.collections[coll_name]

        try:
            count = coll.bulkSave(docs, overwrite=True)
        except UpdateError as ex:
            logger.logger.error(ex)
            return False
        logger.logger.debug('Total {} documents created.'.format(count))

        return True


class ArangoRelationDaoImpl(ArangoBaseDaoImpl, RelationDao):
    def __init__(self, db_conf):
        ArangoBaseDaoImpl.__init__(self, db_conf)

    def add_all(self, ts_sec, relations: List[Relation]) -> bool:
        if not relations:
            return True

        if not self._add_timestamp(ts_sec):
            return False

        coll_edges = {}
        for relation in relations:
            coll_name = relation.type
            coll_edges.setdefault(coll_name, [])
            coll_edges[coll_name].append(transfer_relation_to_edge_dict(relation, ts_sec))

        for coll_name, edges in coll_edges.items():
            if not self.db.hasCollection(coll_name):
                self.db.createCollection(className='Edges', name=coll_name)
            coll: Collection = self.db.collections[coll_name]

            try:
                count = coll.bulkSave(edges)
            except UpdateError as ex:
                logger.logger.error(ex)
                return False
            logger.logger.debug('Total {} edges of {} created.'.format(count, coll_name))

        return True
