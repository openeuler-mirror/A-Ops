import os
from dataclasses import dataclass
from enum import Enum
from typing import List

import yaml


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
    TASK = 'task'
    ENDPOINT = 'endpoint'
    TCP_LINK = 'tcp_link'
    IPVS_LINK = 'ipvs_link'
    NGINX_LINK = 'nginx_link'
    HAPROXY_LINK = 'haproxy_link'


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
class RelationMeta:
    id: str
    layer: str
    from_type: str
    to_type: str


@dataclass
class DirectRelationMeta(RelationMeta):
    matches: List[MatchMeta]
    requires: List[RequireMeta]


@dataclass
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
    value = data.get("value")

    if not RelationSideType.check_value(side):
        print("Unsupported require side.")
        return False

    if not isinstance(label, str):
        print("Require label must be a string.")
        return False

    if value is None:
        print("Require value can't be empty.")
        return False

    return True


def _check_relation_object(data) -> bool:
    if not isinstance(data, dict):
        print("Relation toType must be a dict.")
        return False

    type_ = data.get("type")
    matches = data.get("matches", [])
    requires = data.get("requires", [])

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


class ObserveMetaMgt:
    def __init__(self):
        self.data_agent = ""
        self.observe_meta_map = {}

    def load_from_yaml(self, observe_path: str) -> bool:
        try:
            observe_path = os.path.abspath(observe_path)
            with open(observe_path, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
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
        observe_meta_map = {}
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
        return True

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

                match_objs = []
                require_objs = []
                for match in matches:
                    match_objs.append(MatchMeta(from_=match.get("from"), to=match.get("to")))
                for require in requires:
                    require_objs.append(RequireMeta(side=require.get("side"), label=require.get("label"),
                                                    value=require.get("value")))

                relation_meta = DirectRelationMeta(id=id_, layer=layer, from_type=subject_type,
                                                   to_type=object_type, matches=match_objs,
                                                   requires=require_objs)
            elif layer == RelationLayerType.INDIRECT.value:
                relation_meta = IndirectRelationMeta(id=id_, layer=layer, from_type=subject_type,
                                                     to_type=object_type)
            if relation_meta is not None:
                res.append(relation_meta)

        return res


g_observe_meta_mgt = ObserveMetaMgt()


# TODO : just for test, to delete
if __name__ == '__main__':
    g_observe_meta_mgt.load_from_yaml("../../doc/observe.yaml")
    for k, v in g_observe_meta_mgt.observe_meta_map.items():
        print(k, v)
