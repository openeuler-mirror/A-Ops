import connexion
import six

from spider.models.base_response import BaseResponse  # noqa: E501
from spider.models.entities_response import EntitiesResponse  # noqa: E501
from spider.models.entity import Entity
from spider.models.call import Call
from spider.models.runon import Runon
from spider.models.attr import Attr
from spider import util
from spider.data_process.data_to_entity import node_entity_process
from spider.util.entityid import entity_name

def get_observed_entity_list(timestamp=None):  # noqa: E501
    """get observed entity list

    get observed entity list # noqa: E501

    :param timestamp: the time that cared
    :type timestamp: int

    :rtype: EntitiesResponse
    """
    entities = []
    # obtain tcp_link entities
    edges_table, edges_infos, nodes_table, lb_tables = node_entity_process()
    for key in edges_table.keys():
        if len(edges_table[key]) == 5:
            edge_attrs = []
            left_call = Call(type="PROCESS",
                             id= edges_table[key]['src'])
            right_call = Call(type = "PROCESS",
                              id = edges_table[key]['dst'])

            linkcount_attr = Attr(key = "link_count",
                              value = edges_infos[key][7])
            rx_bytes_attr = Attr(key = "rx_bytes",
                              value = edges_infos[key][0])
            tx_bytes_attr = Attr(key = "tx_bytes",
                              value = edges_infos[key][1])
            edge_attrs.append(linkcount_attr)
            edge_attrs.append(rx_bytes_attr)
            edge_attrs.append(tx_bytes_attr)
            entity = Entity(entityid = edges_table[key]['edge'],
                            type = "TCP-LINK",
                            name = edges_table[key]['edge'],
                            dependeditems = left_call,
                            dependingitems = right_call,
                            attrs = edge_attrs)
            entities.append(entity)
    for key in nodes_table.keys():
        left_calls = []
        right_calls = []
        if nodes_table[key].get('l_edge') is not None:
            left_call = Call(type = nodes_table[key]['l_edge']['type'],
                             id = nodes_table[key]['l_edge']['id'])
            left_calls.append(left_call)
        if nodes_table[key].get('r_edge') is not None:
            right_call = Call(type = nodes_table[key]['r_edge']['type'],
                             id = nodes_table[key]['r_edge']['id'])
            right_calls.append(right_call)
        if nodes_table[key].get('lb_edge') is not None:
            lb_call = Call(type = nodes_table[key]['lb_edge']['type'],
                             id = nodes_table[key]['lb_edge']['id'])
            left_calls.append(lb_call)

        entity = Entity(entityid = key,
                        type = "PROCESS",
                        name = key,
                        dependeditems = left_calls,
                        dependingitems = right_calls)
        entities.append(entity)
    for key in lb_tables.keys():
        right_calls = []
        left_call = Call(type = "PROCESS",
                        id = lb_tables[key]['src'])
        right_call = Call(type = "PROCESS",
                        id = lb_tables[key]['dst'])
        run_on = Runon(type = "PROCESS",
                        id = lb_tables[key]['on'])
        right_calls.append(right_call)
        right_calls.append(run_on)
        entity = Entity(entityid = key,
                        type = "NGINX-LINK",
                        name = lb_tables[key]['lb_id'],
                        dependeditems = left_call,
                        dependingitems = right_calls)
        entities.append(entity)

    entities_res = EntitiesResponse(code = 200,
                                    msg = "option successfully",
                                    timestamp = 111,
                                    entities = entities)
    return entities_res, 200


def get_topo_graph_status():  # noqa: E501
    """get Topo Graph Engine Service health status

    get Topo Graph Engine Service health status # noqa: E501


    :rtype: BaseResponse
    """
    return 'do get_topo_graph_status!'
