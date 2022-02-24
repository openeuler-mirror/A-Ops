from typing import List, Dict, Tuple

from spider.conf.observe_meta import ObserveMetaMgt, ObserveMeta, EntityType
from spider.conf.observe_meta import DirectRelationMeta, RelationSideType, RelationType, RelationLayerType
from .models import ObserveEntity, Relation

ConnectPair = Tuple[ObserveEntity, ObserveEntity]


class ObserveEntityCreator:
    @staticmethod
    def create_observe_entity(entity_type: str, entity_attrs: dict, entity_meta: ObserveMeta = None) -> ObserveEntity:
        """
        根据采集的观测实例数据和对应类型的观测对象配置元数据，创建一个观测实例对象。
        @param entity_type: 观测对象类型
        @param entity_attrs: 观测实例数据
        @param entity_meta: 观测对象配置元数据
        @return: 返回类型为 entity_type 的一个观测对象实例
        """
        if entity_meta is None:
            entity_meta = ObserveMetaMgt().get_observe_meta(entity_type)
            if entity_meta is None:
                return None

        entity = ObserveEntity(type=entity_type,
                               name=entity_attrs.get(entity_meta.name),
                               level=entity_meta.level,
                               timestamp=entity_attrs.get('timestamp'),
                               observe_data=entity_attrs,
                               observe_meta=entity_meta)

        return None if not entity.id else entity

    @staticmethod
    def create_logical_observe_entities(observe_entities: List[ObserveEntity]) -> List[ObserveEntity]:
        res: List[ObserveEntity] = []

        observe_entity_map: Dict[str, List[ObserveEntity]] = {}
        for entity in observe_entities:
            val = observe_entity_map.setdefault(entity.type, [])
            val.append(entity)

        tasks = observe_entity_map.get(EntityType.TASK.value, [])
        app_instances = ObserveEntityCreator._create_app_instance_observe_entities(tasks)
        res.extend(app_instances)

        return res

    @staticmethod
    def _create_app_instance_observe_entities(tasks: List[ObserveEntity]) -> List[ObserveEntity]:
        app_inst_meta = ObserveMetaMgt().get_observe_meta(EntityType.APPINSTANCE.value)
        entity_map: Dict[str, ObserveEntity] = {}

        for task in tasks:
            app_inst_data = {}
            for app_inst_key in app_inst_meta.keys:
                if app_inst_key in task.attrs:
                    app_inst_data[app_inst_key] = task.attrs.get(app_inst_key)
            for app_inst_label in app_inst_meta.labels:
                if app_inst_label in task.attrs:
                    app_inst_data[app_inst_label] = task.attrs.get(app_inst_label)

            entity = ObserveEntity(type=EntityType.APPINSTANCE.value,
                                   name="",
                                   level=app_inst_meta.level,
                                   timestamp=task.timestamp,
                                   observe_data=app_inst_data,
                                   observe_meta=app_inst_meta)
            if not entity.id:
                continue
            entity_map.setdefault(entity.id, entity)
            entity_attrs = entity_map.get(entity.id).attrs
            entity_attrs.setdefault('tasks', [])
            entity_attrs.get('tasks').append(task.id)

        return list(entity_map.values())


class DirectRelationCreator:
    @staticmethod
    def create_relation(sub_entity: ObserveEntity, obj_entity: ObserveEntity,
                        relation_meta: DirectRelationMeta) -> Relation:
        """
        创建一个直接的关联关系。
        @param sub_entity: 关系的主体，是一个观测对象实例
        @param obj_entity: 关系的客体，是一个观测对象实例
        @param relation_meta: 关系的元数据
        @return: 返回一个直接的关联关系
        """
        if sub_entity is None or obj_entity is None or relation_meta is None:
            return None
        if sub_entity.id == obj_entity.id:
            return None
        if sub_entity.type != relation_meta.from_type or obj_entity.type != relation_meta.to_type:
            return None

        for match in relation_meta.matches:
            if sub_entity.attrs.get(match.from_) != obj_entity.attrs.get(match.to):
                return None

        for require in relation_meta.requires:
            entity = sub_entity if RelationSideType.FROM.value == require.side else obj_entity
            if entity.attrs.get(require.label) != require.value:
                return None

        relation = Relation(relation_meta.id, relation_meta.layer, sub_entity, obj_entity)
        return relation

    @staticmethod
    def create_relations(observe_entities: List[ObserveEntity]) -> List[Relation]:
        """
        计算所有观测实例之间的直接关联关系。
        @param observe_entities: 观测实例的集合
        @return: 返回所有观测实例之间存在的直接关联关系的集合
        """
        observe_entity_map: Dict[str, List[ObserveEntity]] = {}
        for entity in observe_entities:
            val = observe_entity_map.setdefault(entity.type, [])
            val.append(entity)

        res: List[Relation] = []
        for sub_entity in observe_entities:
            observe_meta = ObserveMetaMgt().get_observe_meta(sub_entity.type)
            for relation_meta in observe_meta.depending_items:
                if not isinstance(relation_meta, DirectRelationMeta):
                    continue
                obj_entities = observe_entity_map.get(relation_meta.to_type)
                if obj_entities is None:
                    continue
                for obj_entity in obj_entities:
                    relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
                    if relation is not None:
                        res.append(relation)

        return res


class IndirectRelationCreator:
    @staticmethod
    def create_relations(observe_entities: List[ObserveEntity],
                         direct_relations: List[Relation]) -> List[Relation]:
        """
        计算所有观测实例之间的间接关联关系。
        @param observe_entities: 观测实例的集合
        @param direct_relations: 所有观测实例 observe_entities 之间存在的直接关联关系的集合
        @return: 返回所有观测实例之间的间接关联关系的集合
        """
        res: List[Relation] = []

        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        res.extend(connect_relations)

        return res

    @staticmethod
    def create_connect_relation(sub_entity: ObserveEntity, obj_entity: ObserveEntity) -> Relation:
        """
        创建一个间接的 connect 关系。
        @param sub_entity: 关系的主体，是一个观测对象实例
        @param obj_entity: 关系的客体，是一个观测对象实例
        @return: 返回一个间接的连接关系。
        """
        if sub_entity is None or obj_entity is None:
            return None
        if sub_entity.id == obj_entity.id:
            return None
        if not ObserveMetaMgt().check_relation(RelationType.CONNECT.value, RelationLayerType.INDIRECT.value,
                                                 sub_entity.type, obj_entity.type):
            return None

        relation = Relation(RelationType.CONNECT.value, RelationLayerType.INDIRECT.value, sub_entity, obj_entity)
        return relation

    @staticmethod
    def create_connect_relations(observe_entities: List[ObserveEntity],
                                 direct_relations: List[Relation]) -> List[Relation]:
        """
        计算所有观测实例之间的间接的 connect 关系。
        @param observe_entities: 观测实例的集合
        @param direct_relations: 所有观测实例 observe_entities 之间存在的直接关联关系的集合
        @return: 返回所有观测实例之间的间接的 connect 关系的集合
        """
        res: List[Relation] = []
        observe_entity_map: Dict[str, ObserveEntity] = {}
        direct_relation_map: Dict[str, List[Relation]] = {}
        belongs_to_map: Dict[str, Relation] = {}
        runs_on_map: Dict[str, Relation] = {}

        for entity in observe_entities:
            observe_entity_map.setdefault(entity.id, entity)

        for relation in direct_relations:
            val = direct_relation_map.setdefault(relation.type, [])
            val.append(relation)
            if relation.type == RelationType.BELONGS_TO.value:
                belongs_to_map.setdefault(relation.sub_entity.id, relation)
            elif relation.type == RelationType.RUNS_ON.value:
                runs_on_map.setdefault(relation.sub_entity.id, relation)

        connect_pairs = IndirectRelationCreator._create_connect_pairs(direct_relation_map)

        res.extend(IndirectRelationCreator._create_connect_relations_by_belongs_to(connect_pairs, belongs_to_map))
        res.extend(IndirectRelationCreator._create_connect_relations_by_runs_on(res, runs_on_map))

        return res

    @staticmethod
    def _create_connect_pairs(direct_relation_map: Dict[str, List[Relation]]) -> List[ConnectPair]:
        res: List[ConnectPair] = []

        res.extend(IndirectRelationCreator._create_connect_pairs_by_is_peer(direct_relation_map))
        res.extend(IndirectRelationCreator._create_connect_pairs_by_is_client_server(direct_relation_map))

        return res

    @staticmethod
    def _create_connect_pairs_by_is_peer(direct_relation_map: Dict[str, List[Relation]]) -> List[ConnectPair]:
        res: List[ConnectPair] = []

        is_peer_relations = direct_relation_map.get(RelationType.IS_PEER.value, [])
        for is_peer_relation in is_peer_relations:
            res.append((is_peer_relation.sub_entity, is_peer_relation.obj_entity))

        return res

    @staticmethod
    def _create_connect_pairs_by_is_client_server(direct_relation_map: Dict[str, List[Relation]]) -> List[ConnectPair]:
        res: List[ConnectPair] = []

        is_server_relations = direct_relation_map.get(RelationType.IS_SERVER.value, [])
        is_client_relations = direct_relation_map.get(RelationType.IS_CLIENT.value, [])
        for is_server_relation in is_server_relations:
            for is_client_relation in is_client_relations:
                if is_server_relation.obj_entity == is_client_relation.obj_entity:
                    res.append((is_client_relation.sub_entity, is_server_relation.sub_entity))

        return res

    @staticmethod
    def _create_connect_relations_by_belongs_to(connect_pairs: List[ConnectPair],
                                                belongs_to_map: Dict[str, Relation]) -> List[Relation]:
        res: List[Relation] = []
        for entity1, entity2 in connect_pairs:
            belongs_to_entities1 = []
            belongs_to_entities2 = []

            tmp = belongs_to_map.get(entity1.id)
            while tmp is not None:
                belongs_to_entities1.append(tmp.obj_entity)
                tmp = belongs_to_map.get(tmp.obj_entity.id)
            tmp = belongs_to_map.get(entity2.id)
            while tmp is not None:
                belongs_to_entities2.append(tmp.obj_entity)
                tmp = belongs_to_map.get(tmp.obj_entity.id)

            for _entity1 in belongs_to_entities1:
                for _entity2 in belongs_to_entities2:
                    relation = IndirectRelationCreator.create_connect_relation(_entity1, _entity2)
                    if relation is not None:
                        res.append(relation)

        return res

    @staticmethod
    def _create_connect_relations_by_runs_on(connect_relations: List[Relation],
                                             runs_on_map: Dict[str, Relation]) -> List[Relation]:
        res: List[Relation] = []
        for connect_relation in connect_relations:
            runs_on_entities1 = []
            runs_on_entities2 = []

            tmp = runs_on_map.get(connect_relation.sub_entity.id)
            while tmp is not None:
                runs_on_entities1.append(tmp.obj_entity)
                tmp = runs_on_map.get(tmp.obj_entity.id)
            tmp = runs_on_map.get(connect_relation.obj_entity.id)
            while tmp is not None:
                runs_on_entities2.append(tmp.obj_entity)
                tmp = runs_on_map.get(tmp.obj_entity.id)

            for entity1 in runs_on_entities1:
                for entity2 in runs_on_entities2:
                    relation = IndirectRelationCreator.create_connect_relation(entity1, entity2)
                    if relation is not None:
                        res.append(relation)

        return res
