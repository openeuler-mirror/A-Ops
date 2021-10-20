import connexion
import six

from spider.models.base_response import BaseResponse  # noqa: E501
from spider.models.entities_response import EntitiesResponse  # noqa: E501
from spider.models.entity import Entity
from spider.models.dependenceitem import Dependenceitem
from spider.models.call import Call
from spider.models.runon import Runon
from spider.models.attr import Attr
from spider.models.anomalyinfo import AnomalyInfo
from spider import util
from spider.data_process.data_to_entity import node_entity_process
from spider.data_process.data_to_entity import clear_tmp
from anomaly_detection.anomaly_detection import detection
from anomaly_detection.common import g_edges_list

def get_observed_entity_list(timestamp=None):  # noqa: E501
    """get observed entity list

    get observed entity list # noqa: E501

    :param timestamp: the time that cared
    :type timestamp: int

    :rtype: EntitiesResponse
    """
    entities = []
    # obtain tcp_link entities
    _edges_table, _edges_infos, _nodes_table, _lb_tables, _vm_tables = node_entity_process()
    if _edges_table is None:
        return 500
    edges_table, edges_infos, nodes_table, lb_tables, vm_tables = detection(_edges_table, _edges_infos, _nodes_table, _lb_tables, _vm_tables)

    # type = "TCP-LINK",
    for key in edges_table.keys():
        if len(edges_table[key]) < 5:
            continue

        edge_attrs = []
        edge_attrs.append(Attr(key="link_count", value=edges_infos.get(key, {}).get("link_count"), vtype="string"))
        edge_attrs.append(Attr(key="rx_bytes", value=edges_infos.get(key, {}).get("rx_bytes"), vtype="string"))
        edge_attrs.append(Attr(key="tx_bytes", value=edges_infos.get(key, {}).get("tx_bytes"), vtype="string"))
        edge_attrs.append(Attr(key="packets_out", value=edges_infos.get(key, {}).get("packets_out"), vtype="string"))
        edge_attrs.append(Attr(key="packets_in", value=edges_infos.get(key, {}).get("packets_in"), vtype="string"))
        edge_attrs.append(Attr(key="retran_packets", value=edges_infos.get(key, {}).get("retran_packets"), vtype="string"))
        edge_attrs.append(Attr(key="lost_packets", value=edges_infos.get(key, {}).get("lost_packets"), vtype="string"))
        edge_attrs.append(Attr(key="rtt", value=edges_infos.get(key, {}).get("rtt"), vtype="string"))

        left_call = Call(type="PROCESS", id=edges_table[key].get('src'))
        right_call = Call(type="PROCESS", id=edges_table[key].get('dst'))

        _anomaly_infos = []
        this_anomaly_infos = edges_infos.get("key", {}).get("anomaly_infos")
        if this_anomaly_infos:
            for i in this_anomaly_infos:
                _anomaly_infos.append(AnomalyInfo(anomaly_attr = i.get("anomaly_attr"), anomaly_type = i.get("anomaly_type")))


        entity = Entity(entityid = edges_table[key].get("edge"),
                        type = "TCP-LINK",
                        name = edges_table[key].get("edge"),
                        dependeditems = Dependenceitem(calls = left_call),
                        dependingitems = Dependenceitem(calls = right_call),
                        attrs = edge_attrs,
                        anomaly_infos = _anomaly_infos,
                        status = edges_table.get(key, {}).get("status"))
        entities.append(entity)
        
    for key in nodes_table.keys():
        left_calls = []
        right_calls = []
        lb_runons = []
        node_attrs = []
        if nodes_table[key].get('l_edge') is not None:
            for i in range(len(nodes_table[key]['l_edge'])):
                val = nodes_table[key]['l_edge'].pop()
                left_call = Call(type = val[1],
                                id = val[0])
                left_calls.append(left_call)
        if nodes_table[key].get('r_edge') is not None:
            for i in range(len(nodes_table[key]['r_edge'])):
                val = nodes_table[key]['r_edge'].pop()
                right_call = Call(type = val[1],
                                id = val[0])
                right_calls.append(right_call)
        if nodes_table[key].get('lb_edge') is not None:
            for i in range(len(nodes_table[key]['lb_edge'])):
                val = nodes_table[key]['lb_edge'].pop()
                lb_runon = Runon(type = val[1],
                                id = val[0])
                lb_runons.append(lb_runon)
        on_runon = Runon(type = "VM", id = nodes_table[key]['host'])
        node_attrs.append(Attr(key = 'example', value = "0xabcd", vtype = "int"))
        entity = Entity(entityid = key,
                        type = "PROCESS",
                        name = key,
                        dependeditems = Dependenceitem(calls = left_calls, run_ons = lb_runons),
                        dependingitems = Dependenceitem(calls = right_calls, run_ons = on_runon),
                        attrs = node_attrs)
        entities.append(entity)
    if lb_tables is not None:
        for key in lb_tables.keys():
            if len(lb_tables[key]) < 5:
                continue
            lb_attrs = []
            left_call = Call(type = "PROCESS",
                            id = lb_tables[key]['src'])
            right_call = Call(type = "PROCESS",
                            id = lb_tables[key]['dst'])
            run_on = Runon(type = "PROCESS",
                            id = lb_tables[key]['on'])
            lb_attrs.append(Attr(key='example', value = "0.1", vtype = "float"))
            entity = Entity(entityid = lb_tables[key]['lb_id'],
                            type = lb_tables[key]['tname'].upper(),
                            name = lb_tables[key]['lb_id'],
                            dependeditems = Dependenceitem(calls = left_call),
                            dependingitems = Dependenceitem(calls = right_call, run_ons = run_on))
            entities.append(entity)

    # type = "VM" 
    for key in vm_tables.keys():
        procs = []
        for i in range(len(vm_tables[key]['proc'])):
            val = vm_tables[key]['proc'].pop()
            proc = Runon(type = "PROCESS",
                         id = val)
            procs.append(proc)
            entity = Entity(entityid = key,
                            type = "VM",
                            name = key,
                            dependeditems = Dependenceitem(run_ons = procs),
                            dependingitems = Dependenceitem())
        entities.append(entity)

    if len(entities) == 0:
        code = 500
        msg = "Empty"
    else:
        code = 200
        msg = "Successful"
    entities_res = EntitiesResponse(code = code,
                                    msg = msg,
                                    timestamp = 12345678,
                                    entities = entities)
    #clear_tmp()
    return entities_res, 200


def get_topo_graph_status():  # noqa: E501
    """get Topo Graph Engine Service health status

    get Topo Graph Engine Service health status # noqa: E501


    :rtype: BaseResponse
    """

    clear_tmp()
    return 'clear tmp files!'
