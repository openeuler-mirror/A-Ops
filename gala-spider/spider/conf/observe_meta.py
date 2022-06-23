import os
from enum import Enum
from typing import List
from typing import Dict
from typing import Set
from dataclasses import dataclass
from dataclasses import field

import yaml

from spider.util.singleton import Singleton


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
    PROCESS = 'system_proc'
    THREAD = 'thread'
    BIND = 'bind'
    UDP = 'udp'
    CONNECT = 'connect'
    LISTEN = 'listen'
    TCP_LINK = 'tcp_link'
    IPVS_LINK = 'ipvs_link'
    NGINX_LINK = 'nginx_link'
    HAPROXY_LINK = 'haproxy_link'
    REDIS_CLIENT = 'redis_client'
    REDIS_SLI = 'ksliprobe'


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
    CONTAINER = 'CONTAINER'
    APPLICATION = 'APPLICATION'
    RUNTIME = 'RUNTIME'
    PROCESS = 'PROCESS'
    RPC = 'RPC'
    LB = 'LB'
    MB = 'MB'


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
    name: str
    level: str
    depending_items: List[RelationMeta]


def _check_relation_match(data) -> bool:
    if not isinstance(data, dict):
        print("Relation match must be a dict.")
        return False

    from_ = data.get("from")
    to = data.get("to")

    if not isinstance(from_, str):
        print("Match from must be a string.")
        return False

    if not isinstance(to, str):
        print("Match to must be a string.")
        return False

    return True


def _check_relation_require(data) -> bool:
    if not isinstance(data, dict):
        print("Relation require must be a dict.")
        return False

    side = data.get("side")
    label = data.get("label")

    if not RelationSideType.check_value(side):
        print("Unsupported require side.")
        return False

    if not isinstance(label, str):
        print("Require label must be a string.")
        return False

    if "value" not in data:
        print("Require value must be set.")
        return False

    return True


def _check_relation_conflict(data) -> bool:
    if not isinstance(data, dict):
        print("Relation conflict must be a dict.")
        return False

    from_ = data.get("from")
    to = data.get("to")

    if not isinstance(from_, str):
        print("Conflict from must be a string.")
        return False

    if not isinstance(to, str):
        print("Conflict to must be a string.")
        return False

    return True


def _check_relation_object(data) -> bool:
    if not isinstance(data, dict):
        print("Relation toType must be a dict.")
        return False

    type_ = data.get("type")
    matches = data.get("matches", [])
    requires = data.get("requires", [])
    conflicts = data.get("conflicts", [])

    if not EntityType.check_value(type_):
        print("Unsupported relation object type: {}".format(type_))
        return False

    if not isinstance(matches, list):
        print("Relation matches must be a list.")
        return False
    for match in matches:
        if not _check_relation_match(match):
            print("Relation match check failed, which is: {}.".format(match))
            return False

    if not isinstance(requires, list):
        print("Relation requires must be a list.")
        return False
    for require in requires:
        if not _check_relation_require(require):
            print("Relation require check failed, which is: {}.".format(require))
            return False

    if not isinstance(conflicts, list):
        print("Relation conflicts must be a list.")
        return False
    for conflict in conflicts:
        if not _check_relation_conflict(conflict):
            print("Relation conflict check failed, which is: {}.".format(conflict))
            return False

    return True


def _check_depending_item(data) -> bool:
    if not isinstance(data, dict):
        print("Entity depending item must be a dict.")
        return False

    id_ = data.get("id")
    layer = data.get("layer")
    to_types = data.get("toTypes")

    if not RelationType.check_value(id_):
        print("Unsupported relation type: {}.".format(id_))
        return False

    if not RelationLayerType.check_value(layer):
        print("Unsupported relation layer: {}.".format(layer))
        return False

    if not isinstance(to_types, list):
        print("Relation toTypes must be a list.")
        return False
    if len(to_types) == 0:
        print("Relation toTypes can't be empty")
        return False
    for to_type in to_types:
        if not _check_relation_object(to_type):
            print("Relation toType check failed, to_type is: {}.".format(to_type))
            return False

    return True


def _check_observe_entity(data) -> bool:
    if not isinstance(data, dict):
        print("Entity must be a dict.")
        return False

    type_ = data.get("type")
    keys = data.get("keys")
    labels = data.get("labels", [])
    name = data.get("name", "")
    metrics = data.get("metrics", [])
    level = data.get("level", "")
    depending_items = data.get("dependingitems", [])

    if not EntityType.check_value(type_):
        print("Unsupported entity type: {}.".format(type_))
        return False

    if not isinstance(keys, list):
        print("Entity keys must be a list.")
        return False
    if len(keys) == 0:
        print("Entity keys can't be empty.")
        return False

    if not isinstance(labels, list):
        print("Entity labels must be a list.")
        return False

    if not isinstance(name, str):
        print("Entity name must be a string.")
        return False

    if not isinstance(metrics, list):
        print("Entity metrics must be a list.")
        return False

    if level and not TopologyLevelType.check_value(level):
        print("Unsupported topology level: {}.".format(level))
        return False

    if not isinstance(depending_items, list):
        print("Entity depending_items must be a list.")
        return False
    for depending_item in depending_items:
        if not _check_depending_item(depending_item):
            print("Entity depending item check failed, which is: {}.".format(depending_item))
            return False

    return True


def _check_yaml_type(data) -> bool:
    data_agent = data.get("data_agent")
    observe_entities = data.get("observe_entities", [])

    if not isinstance(data_agent, str):
        print("Data_agent must be a string.")
        return False

    if not isinstance(observe_entities, list):
        print("Observe_entities must be a list.")
        return False
    for item in observe_entities:
        if not _check_observe_entity(item):
            print("Observe entity check failed, which is: {}.".format(item))
            return False

    return True


class ObserveMetaMgt(metaclass=Singleton):
    def __init__(self):
        self.data_agent = ""
        self.observe_meta_map: Dict[str, ObserveMeta] = {}
        self.relation_meta_set: Set[RelationMeta] = set()

    def load_from_yaml(self, observe_path: str) -> bool:
        try:
            observe_path = os.path.abspath(observe_path)
            with open(observe_path, 'r') as file:
                data = yaml.safe_load(file)
        except IOError as ex:
            print("Unable to open observe config file: {}.".format(ex))
            return False

        if not _check_yaml_type(data):
            print("Observe config file check failed: {}.".format(observe_path))
            return False

        data_agent = data.get("data_agent")
        if not data_agent:
            print("No data agent set.")
            return False

        observe_entities = data.get("observe_entities", [])
        observe_meta_map: Dict[str, ObserveMeta] = {}
        for item in observe_entities:
            entity_type = item.get("type")
            if entity_type in observe_meta_map:
                print("Duplicate observe entity type defined: {}.".format(entity_type))
                return False
            observe_meta = ObserveMetaMgt._get_observe_meta_from_dict(item)
            if observe_meta is None:
                print("Observe metadata config error.")
                return False
            observe_meta_map.setdefault(entity_type, observe_meta)

        self.data_agent = data_agent
        self.observe_meta_map = observe_meta_map
        for observe_meta in self.observe_meta_map.values():
            for relation_meta in observe_meta.depending_items:
                self.relation_meta_set.add(relation_meta)

        return True

    def get_observe_meta(self, entity_type: str) -> ObserveMeta:
        return self.observe_meta_map.get(entity_type)

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
        type_ = data.get("type")
        keys = data.get("keys")
        labels = data.get("labels", [])
        name = data.get("name")
        metrics = data.get("metrics", [])
        level = data.get("level")
        depending_items = data.get("dependingitems", [])

        keys.sort()
        labels.sort()
        metrics.sort()

        depending_objs = []
        for depending_item in depending_items:
            tmp_depending_objs = ObserveMetaMgt._get_depending_items_from_dict(depending_item, type_)
            depending_objs.extend(tmp_depending_objs)

        return ObserveMeta(
            type=type_,
            keys=keys,
            labels=labels,
            name=name,
            metrics=metrics,
            level=level,
            depending_items=depending_objs
        )

    @staticmethod
    def _get_depending_items_from_dict(data: dict, subject_type: str) -> List[RelationMeta]:
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


def init_observe_meta_config(observe_conf_path) -> bool:
    observe_meta_mgt = ObserveMetaMgt()
    if not observe_meta_mgt.load_from_yaml(observe_conf_path):
        return False
    return True
