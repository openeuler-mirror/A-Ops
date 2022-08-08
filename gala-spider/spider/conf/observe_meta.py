import os
from enum import Enum
from typing import List
from typing import Dict
from typing import Set
from dataclasses import dataclass
from dataclasses import field

import yaml

from spider.util.singleton import Singleton
from spider.util import logger
from spider.exceptions import MetadataException


class ValueCheckEnum(Enum):
    @classmethod
    def check_value(cls, value) -> bool:
        for v in cls.__members__.values():
            if v.value == value:
                return True
        return False


class EntityType(ValueCheckEnum):
    HOST = 'host'
    CONTAINER = 'container'
    APPINSTANCE = 'appinstance'
    PROCESS = 'proc'
    THREAD = 'thread'
    ENDPOINT = 'endpoint'
    TCP_LINK = 'tcp_link'
    IPVS_LINK = 'ipvs_link'
    NGINX_LINK = 'nginx_link'
    HAPROXY_LINK = 'haproxy_link'
    REDIS_CLIENT = 'redis_client'
    REDIS_SLI = 'sli'
    DISK = 'disk'
    BLOCK = 'block'
    NETCARD = 'nic'
    CPU = 'cpu'


class RelationType(ValueCheckEnum):
    RUNS_ON = 'runs_on'
    BELONGS_TO = 'belongs_to'
    IS_SERVER = 'is_server'
    IS_CLIENT = 'is_client'
    IS_PEER = 'is_peer'
    CONNECT = 'connect'


class RelationLayerType(ValueCheckEnum):
    DIRECT = 'direct'
    INDIRECT = 'indirect'


class RelationSideType(ValueCheckEnum):
    FROM = 'from'
    TO = 'to'


class TopologyLevelType(ValueCheckEnum):
    HOST = 'HOST'
    PROCESS = 'PROCESS'
    RPC = 'RPC'


entity_level_map = {
    # HOST level
    EntityType.HOST.value: TopologyLevelType.HOST.value,
    EntityType.NETCARD.value: TopologyLevelType.HOST.value,
    EntityType.CPU.value: TopologyLevelType.HOST.value,
    EntityType.DISK.value: TopologyLevelType.HOST.value,
    EntityType.BLOCK.value: TopologyLevelType.HOST.value,
    # PROCESS level
    EntityType.PROCESS.value: TopologyLevelType.PROCESS.value,
    EntityType.THREAD.value: TopologyLevelType.PROCESS.value,
    EntityType.CONTAINER.value: TopologyLevelType.PROCESS.value,
    EntityType.APPINSTANCE.value: TopologyLevelType.PROCESS.value,
    EntityType.ENDPOINT.value: TopologyLevelType.PROCESS.value,
    EntityType.REDIS_SLI.value: TopologyLevelType.PROCESS.value,
    # RPC level
    EntityType.TCP_LINK.value: TopologyLevelType.RPC.value,
    EntityType.HAPROXY_LINK.value: TopologyLevelType.RPC.value,
    EntityType.IPVS_LINK.value: TopologyLevelType.RPC.value,
    EntityType.NGINX_LINK.value: TopologyLevelType.RPC.value,
}


def get_entity_topo_level(entity_type):
    return entity_level_map.get(entity_type)


@dataclass
class MatchMeta:
    from_: str
    to: str


@dataclass
class RequireMeta:
    side: str
    label: str
    value: str


@dataclass
class ConflictMeta:
    from_: str
    to: str


@dataclass(unsafe_hash=True)
class RelationMeta:
    id: str
    layer: str
    from_type: str
    to_type: str


@dataclass(unsafe_hash=True)
class DirectRelationMeta(RelationMeta):
    matches: List[MatchMeta] = field(compare=False)
    requires: List[RequireMeta] = field(default_factory=list, compare=False)
    conflicts: List[ConflictMeta] = field(default_factory=list, compare=False)


@dataclass(unsafe_hash=True)
class IndirectRelationMeta(RelationMeta):
    pass


@dataclass
class ObserveMeta:
    type: str
    keys: List[str]
    labels: List[str]
    metrics: List[str]
    name: str = ''
    level: str = ''
    version: str = ''
    depending_items: List[RelationMeta] = field(default_factory=list)

    def ver_cmp(self, another) -> int:
        if not isinstance(another, ObserveMeta):
            raise TypeError('The type of the param another is not ObserverMeta.')
        if self.version < another.version:
            return -1
        elif self.version == another.version:
            return 0
        else:
            return 1


def _check_relation_match(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Relation match must be a dict.")
        return False

    from_ = data.get("from")
    to = data.get("to")

    if not isinstance(from_, str):
        logger.logger.error("Match from must be a string.")
        return False

    if not isinstance(to, str):
        logger.logger.error("Match to must be a string.")
        return False

    return True


def _check_relation_require(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Relation require must be a dict.")
        return False

    side = data.get("side")
    label = data.get("label")

    if not RelationSideType.check_value(side):
        logger.logger.error("Unsupported require side.")
        return False

    if not isinstance(label, str):
        logger.logger.error("Require label must be a string.")
        return False

    if "value" not in data:
        logger.logger.error("Require value must be set.")
        return False

    return True


def _check_relation_conflict(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Relation conflict must be a dict.")
        return False

    from_ = data.get("from")
    to = data.get("to")

    if not isinstance(from_, str):
        logger.logger.error("Conflict from must be a string.")
        return False

    if not isinstance(to, str):
        logger.logger.error("Conflict to must be a string.")
        return False

    return True


def _check_relation_object(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Relation toType must be a dict.")
        return False

    type_ = data.get("type")
    matches = data.get("matches", [])
    requires = data.get("requires", [])
    conflicts = data.get("conflicts", [])

    if not EntityType.check_value(type_):
        logger.logger.error("Unsupported relation object type: {}".format(type_))
        return False

    if not isinstance(matches, list):
        logger.logger.error("Relation matches must be a list.")
        return False
    for match in matches:
        if not _check_relation_match(match):
            logger.logger.error("Relation match check failed, which is: {}.".format(match))
            return False

    if not isinstance(requires, list):
        logger.logger.error("Relation requires must be a list.")
        return False
    for require in requires:
        if not _check_relation_require(require):
            logger.logger.error("Relation require check failed, which is: {}.".format(require))
            return False

    if not isinstance(conflicts, list):
        logger.logger.error("Relation conflicts must be a list.")
        return False
    for conflict in conflicts:
        if not _check_relation_conflict(conflict):
            logger.logger.error("Relation conflict check failed, which is: {}.".format(conflict))
            return False

    return True


def _check_depending_item(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Entity depending item must be a dict.")
        return False

    id_ = data.get("id")
    layer = data.get("layer")
    to_types = data.get("toTypes")

    if not RelationType.check_value(id_):
        logger.logger.error("Unsupported relation type: {}.".format(id_))
        return False

    if not RelationLayerType.check_value(layer):
        logger.logger.error("Unsupported relation layer: {}.".format(layer))
        return False

    if not isinstance(to_types, list):
        logger.logger.error("Relation toTypes must be a list.")
        return False
    if len(to_types) == 0:
        logger.logger.error("Relation toTypes can't be empty")
        return False
    for to_type in to_types:
        if not _check_relation_object(to_type):
            logger.logger.error("Relation toType check failed, to_type is: {}.".format(to_type))
            return False

    return True


def _check_depending_items(data) -> bool:
    if not isinstance(data, list):
        logger.logger.error("Entity depending items must be a list.")
        return False

    for depending_item in data:
        if not _check_depending_item(depending_item):
            logger.logger.error("Entity depending item check failed, which is: {}.".format(depending_item))
            return False

    return True


def _check_relation(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Relation must be a dict.")
        return False

    from_type = data.get("type", "")
    depending_items = data.get("dependingitems", [])

    if not EntityType.check_value(from_type):
        logger.logger.error("From type of the relation must be not empty.")
        return False

    if not _check_depending_items(depending_items):
        return False

    return True


def _check_observe_entity(data) -> bool:
    if not isinstance(data, dict):
        logger.logger.error("Entity must be a dict.")
        return False

    type_ = data.get("type")
    keys = data.get("keys")
    labels = data.get("labels", [])
    metrics = data.get("metrics", [])

    if not EntityType.check_value(type_):
        logger.logger.error("Unsupported entity type: {}.".format(type_))
        return False

    if not isinstance(keys, list):
        logger.logger.error("Entity keys must be a list.")
        return False
    if len(keys) == 0:
        logger.logger.error("Entity keys can't be empty.")
        return False

    if not isinstance(labels, list):
        logger.logger.error("Entity labels must be a list.")
        return False

    if not isinstance(metrics, list):
        logger.logger.error("Entity metrics must be a list.")
        return False

    return True


def _check_observe_meta_yaml_type(data) -> bool:
    observe_entities = data.get("observe_entities", [])

    if not isinstance(observe_entities, list):
        logger.logger.error("Observe_entities must be a list.")
        return False
    for item in observe_entities:
        if not _check_observe_entity(item):
            logger.logger.error("Observe entity check failed, which is: {}.".format(item))
            return False

    return True


def _check_relation_yaml_type(data) -> bool:
    relations = data.get("topo_relations")

    if not isinstance(relations, list):
        logger.logger.error("Relations must be a list.")
        return False

    for relation in relations:
        if not _check_relation(relation):
            logger.logger.error("Relation check failed, which is: {}.".format(relation))
            return False

    return True


def _merge_tcp_link_meta(old_obsv_meta, new_obsv_meta):
    metric_set = set(old_obsv_meta.metrics)
    for metric in new_obsv_meta.metrics:
        if metric not in metric_set:
            old_obsv_meta.metrics.append(metric)


def check_meta(old_obsv_meta: ObserveMeta, new_obsv_meta: ObserveMeta):
    # check keys
    if len(old_obsv_meta.keys) != len(new_obsv_meta.keys):
        raise MetadataException('Keys of metadata not consistent')
    for k1, k2 in zip(old_obsv_meta.keys, new_obsv_meta.keys):
        if k1 != k2:
            raise MetadataException('Keys of metadata not consistent')
    # check metrics
    metric_set = set(old_obsv_meta.metrics)
    for metric in new_obsv_meta.metrics:
        if metric in metric_set:
            raise MetadataException('Metric name {} of metadata duplicate'.format(metric))


def merge_meta(old_obsv_meta: ObserveMeta, new_obsv_meta: ObserveMeta) -> ObserveMeta:
    merged_labels = list(set(old_obsv_meta.labels + new_obsv_meta.labels))
    merged_metrics = old_obsv_meta.metrics + new_obsv_meta.metrics
    obsv_meta = ObserveMeta(
        type=old_obsv_meta.type,
        keys=old_obsv_meta.keys,
        labels=merged_labels,
        metrics=merged_metrics,
        name=old_obsv_meta.name,
        level=old_obsv_meta.level,
        version=old_obsv_meta.version,
        depending_items=old_obsv_meta.depending_items,
    )
    return obsv_meta


class ObserveMetaMgt(metaclass=Singleton):
    def __init__(self):
        self.data_agent = ""
        self.observe_meta_map: Dict[str, ObserveMeta] = {}
        self.relation_meta_set: Set[RelationMeta] = set()
        self.sub_relations: Dict[str, RelationMeta] = {}
        self._merged_tables: Dict[str, set] = {}

    def set_data_agent(self, data_agent):
        self.data_agent = data_agent

    def load_ext_observe_meta_from_yaml(self, observe_path: str) -> bool:
        observe_path = os.path.abspath(observe_path)
        if not os.path.exists(observe_path):
            return True

        try:
            with open(observe_path, 'r') as file:
                data = yaml.safe_load(file)
        except IOError as ex:
            logger.logger.error("Unable to open observe config file: {}.".format(ex))
            return False

        if not _check_observe_meta_yaml_type(data):
            logger.logger.error("Observe config file check failed: {}.".format(observe_path))
            return False

        observe_entities = data.get("observe_entities", [])
        for item in observe_entities:
            entity_type = item.get("type")
            if entity_type in self.observe_meta_map:
                logger.logger.error("Duplicate observe entity type defined: {}.".format(entity_type))
                return False
            observe_meta = ObserveMetaMgt._get_observe_meta_from_dict(item)
            if observe_meta is None:
                logger.logger.error("Observe metadata config error.")
                return False
            observe_meta.depending_items = self.sub_relations.get(entity_type, [])
            self.observe_meta_map.setdefault(entity_type, observe_meta)

        return True

    def load_topo_relation_from_yaml(self, relation_path: str) -> bool:
        relation_path = os.path.abspath(relation_path)
        if not os.path.exists(relation_path):
            return True

        try:
            with open(relation_path, 'r') as file:
                data = yaml.safe_load(file)
        except IOError as ex:
            logger.logger.error("Unable to open relation config file: {}.".format(ex))
            return False

        if not _check_relation_yaml_type(data):
            logger.logger.error("Observe config file check failed: {}.".format(relation_path))
            return False

        topo_relations = data.get("topo_relations", [])
        sub_relations = {}
        relation_meta_set = set()
        for item in topo_relations:
            sub_type = item.get("type")
            depending_items = item.get("dependingitems", [])

            all_depending_metas = []
            for depending_item in depending_items:
                depending_metas = ObserveMetaMgt._get_relations_from_dict(depending_item, sub_type)
                all_depending_metas.extend(depending_metas)

            for depending_meta in all_depending_metas:
                if depending_meta in relation_meta_set:
                    continue
                relation_meta_set.add(depending_meta)
                one_type_relations = sub_relations.setdefault(depending_meta.from_type, [])
                one_type_relations.append(depending_meta)

        self.relation_meta_set = relation_meta_set
        self.sub_relations = sub_relations

        return True

    def add_observe_meta_from_dict(self, data: dict):
        data['type'] = data.get('entity_name')
        if not data['type']:
            return
        if not EntityType.check_value(data.get('type')):
            logger.logger.warning('Unsupported entity type {}, ignore it'.format(data.get('type')))
            return
        table_name = data.get('meta_name')

        observe_meta = ObserveMetaMgt._get_observe_meta_from_dict(data)
        if observe_meta.type not in self.observe_meta_map:
            observe_meta.depending_items = self.get_depending_relations(observe_meta.type)
            self.observe_meta_map.setdefault(observe_meta.type, observe_meta)
            tables = self._merged_tables.setdefault(observe_meta.type, set())
            tables.add(table_name)
            return

        old_observe_meta = self.observe_meta_map.get(observe_meta.type)
        if old_observe_meta.ver_cmp(observe_meta) < 0:
            observe_meta.depending_items = old_observe_meta.depending_items
            self.observe_meta_map.update({observe_meta.type: observe_meta})
            self._merged_tables.update({observe_meta.type: {table_name}})
        elif old_observe_meta.ver_cmp(observe_meta) == 0:
            if table_name in self._merged_tables.get(observe_meta.type):
                return
            try:
                check_meta(old_observe_meta, observe_meta)
            except MetadataException as ex:
                logger.logger.warning(
                    'Metadata of entity type {} merged failed, because {}'.format(observe_meta.type, ex)
                )
                del self.observe_meta_map[observe_meta.type]
                del self._merged_tables[observe_meta.type]
                return
            new_obsv_meta = merge_meta(old_observe_meta, observe_meta)
            self.observe_meta_map.update({observe_meta.type: new_obsv_meta})
            self._merged_tables.get(observe_meta.type).add(table_name)
            return

    def get_observe_meta(self, entity_type: str) -> ObserveMeta:
        return self.observe_meta_map.get(entity_type)

    def get_depending_relations(self, entity_type: str) -> List[RelationMeta]:
        return self.sub_relations.get(entity_type, [])

    def check_relation(self, relation_id: str, layer: str, from_type: str, to_type: str) -> bool:
        relation_meta = None
        if layer == RelationLayerType.DIRECT.value:
            relation_meta = DirectRelationMeta(relation_id, layer, from_type, to_type)
        elif layer == RelationLayerType.INDIRECT.value:
            relation_meta = IndirectRelationMeta(relation_id, layer, from_type, to_type)

        if relation_meta in self.relation_meta_set:
            return True
        return False

    @staticmethod
    def _get_observe_meta_from_dict(data: dict) -> ObserveMeta:
        type_ = data.get("type", "")
        keys = data.get("keys", [])
        labels = data.get("labels", [])
        metrics = data.get("metrics", [])
        version = data.get("version", "")

        return ObserveMeta(
            type=type_,
            keys=keys,
            labels=labels,
            metrics=metrics,
            level=get_entity_topo_level(type_),
            version=version
        )

    @staticmethod
    def _get_relations_from_dict(data: dict, subject_type: str) -> List[RelationMeta]:
        res = []

        id_ = data.get("id")
        layer = data.get("layer")
        to_types = data.get("toTypes")

        for to_type in to_types:
            object_type = to_type.get("type")

            relation_meta = None
            if layer == RelationLayerType.DIRECT.value:
                matches = to_type.get("matches", [])
                requires = to_type.get("requires", [])
                conflicts = to_type.get("conflicts", [])

                match_objs = []
                require_objs = []
                conflict_objs = []
                for match in matches:
                    match_objs.append(MatchMeta(from_=match.get("from"), to=match.get("to")))
                for require in requires:
                    require_objs.append(RequireMeta(side=require.get("side"), label=require.get("label"),
                                                    value=require.get("value")))
                for conflict in conflicts:
                    conflict_objs.append(ConflictMeta(from_=conflict.get("from"), to=conflict.get("to")))

                relation_meta = DirectRelationMeta(id=id_, layer=layer, from_type=subject_type,
                                                   to_type=object_type, matches=match_objs,
                                                   requires=require_objs, conflicts=conflict_objs)
            elif layer == RelationLayerType.INDIRECT.value:
                relation_meta = IndirectRelationMeta(id=id_, layer=layer, from_type=subject_type,
                                                     to_type=object_type)
            if relation_meta is not None:
                res.append(relation_meta)

        return res


def init_observe_meta_config(data_agent, ext_observe_meta_path=None, topo_relation_path=None) -> bool:
    observe_meta_mgt = ObserveMetaMgt()
    observe_meta_mgt.set_data_agent(data_agent)
    if topo_relation_path is not None:
        if not observe_meta_mgt.load_topo_relation_from_yaml(topo_relation_path):
            return False
    # 注意：拓扑关系的初始化要先于观测对象元数据初始化，否则可能导致观察对象的拓扑关系为空
    if ext_observe_meta_path is not None:
        if not observe_meta_mgt.load_ext_observe_meta_from_yaml(ext_observe_meta_path):
            return False
    return True
