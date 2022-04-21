from typing import Dict
from typing import List

from spider.conf import SpiderConfig
from spider.util import logger
from spider.data_process import DataProcessorFactory
from spider.models import BaseResponse
from spider.models import EntitiesResponse
from spider.models import Entity
from spider.models import Dependenceitem
from spider.models import Attr
from spider.entity_mgt import ObserveEntity
from spider.entity_mgt import Relation
from spider.service import DataCollectionService
from spider.service import CalculationService


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
    db_agent = SpiderConfig().db_agent
    data_processor = DataProcessorFactory.get_instance(db_agent)
    if data_processor is None:
        logger.logger.error("Unknown data source:{}, please check!".format(db_agent))
        return
    collect_srv = DataCollectionService(data_processor)
    calc_srv = CalculationService()
    observe_entities = collect_srv.get_observe_entities(timestamp)
    relations = calc_srv.get_all_relations(observe_entities)

    # transfer observe entities to response format
    resp_entity_map = _get_response_entities(observe_entities)
    _append_dependence_info(resp_entity_map, relations)

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
