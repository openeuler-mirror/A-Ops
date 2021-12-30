from typing import Dict, List
import time

from spider.models import BaseResponse, EntitiesResponse, Entity, Dependenceitem, Attr
from spider.util import conf
from spider.entity_mgt import ObserveEntity, Relation
from spider.entity_mgt import DirectRelationCreator, IndirectRelationCreator
from spider.data_process.prometheus_processor import g_prometheus_processor


def _get_observe_entities(timestamp=None) -> List[ObserveEntity]:
    entities: List[ObserveEntity] = []
    db_agent = conf.db_agent

    if db_agent == "prometheus":
        entities = g_prometheus_processor.get_observe_entities(timestamp)
    elif db_agent == "kafka":
        # TODO: get entities from kafka
        pass
    else:
        print("Unknown data source:{}, please check!".format(db_agent))

    return entities


def _get_entity_relations(observe_entities: List[ObserveEntity]) -> List[Relation]:
    res: List[Relation] = []

    direct_relations = DirectRelationCreator.create_relations(observe_entities)
    res.extend(direct_relations)
    indirect_relations = IndirectRelationCreator.create_relations(observe_entities, direct_relations)
    res.extend(indirect_relations)

    return res


def _get_response_entities(observe_entities: List[ObserveEntity]) -> Dict[str, Entity]:
    res: Dict[str, Entity] = {}

    for observe_entity in observe_entities:
        attrs = []
        for attr_key, attr_val in observe_entity.attrs.items():
            attrs.append(Attr(attr_key, attr_val, 'string'))

        entity = Entity(entityid=observe_entity.id,
                        type=observe_entity.type,
                        name=observe_entity.name,
                        level=observe_entity.level,
                        dependingitems=[],
                        dependeditems=[],
                        attrs=attrs)
        res.setdefault(observe_entity.id, entity)

    return res


def _append_dependence_info(resp_entity_map: Dict[str, Entity], relations: List[Relation]):
    for relation in relations:
        depending_item = Dependenceitem(relation_id=relation.type, layer=relation.layer,
                                        target={'type': relation.obj_entity.type, 'entityid': relation.obj_entity.id})
        if relation.sub_entity.id in resp_entity_map:
            resp_entity_map.get(relation.sub_entity.id).dependingitems.append(depending_item)

        depended_item = Dependenceitem(relation_id=relation.type, layer=relation.layer,
                                       target={'type': relation.sub_entity.type, 'entityid': relation.sub_entity.id})
        if relation.obj_entity.id in resp_entity_map:
            resp_entity_map.get(relation.obj_entity.id).dependeditems.append(depended_item)


def get_observed_entity_list(timestamp=None):  # noqa: E501
    """get observed entity list

    get observed entity list # noqa: E501

    :param timestamp: the time that cared
    :type timestamp: int

    :rtype: EntitiesResponse
    """
    # obtain observe entities
    observe_entities = _get_observe_entities(timestamp)
    relations = _get_entity_relations(observe_entities)

    # TODO: anomaly detect

    # transfer observe entities to response format
    resp_entity_map = _get_response_entities(observe_entities)
    _append_dependence_info(resp_entity_map, relations)

    # TODO: add anomaly info

    if len(resp_entity_map) == 0:
        code = 500
        msg = "Empty"
        timestamp = None
    else:
        code = 200
        msg = "Successful"
        timestamp = observe_entities[0].timestamp

    entity_ids = []
    resp_entities = []
    for k, v in resp_entity_map.items():
        entity_ids.append(k)
        resp_entities.append(v)

    entities_res = EntitiesResponse(code=code,
                                    msg=msg,
                                    timestamp=timestamp,
                                    entityids=entity_ids,
                                    entities=resp_entities)

    return entities_res, 200


def get_topo_graph_status():  # noqa: E501
    """get Topo Graph Engine Service health status

    get Topo Graph Engine Service health status # noqa: E501


    :rtype: BaseResponse
    """

    return ''
