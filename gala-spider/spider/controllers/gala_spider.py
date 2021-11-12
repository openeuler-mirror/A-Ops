from dataclasses import asdict
from typing import Dict, List

from spider.models.base_response import BaseResponse  # noqa: E501
from spider.models.entities_response import EntitiesResponse  # noqa: E501
from spider.models.entity import Entity
from spider.models.dependenceitem import Dependenceitem
from spider.models.call import Call
from spider.models.runon import Runon
from spider.models.attr import Attr
from spider.models.anomalyinfo import AnomalyInfo
from spider.data_process.data_to_entity import node_entity_process
from spider.data_process.data_to_entity import clear_tmp
from anomaly_detection.anomaly_detection import detection
from spider.data_process.models import HostNode, ProcessNode
from spider.data_process.models import LbLinkInfo, LbLinkKey
from spider.data_process.models import TcpLinkKey, TcpLinkInfo


def get_tcp_link_entities(link_infos: Dict[TcpLinkKey, TcpLinkInfo], anomaly_infos) -> List[Entity]:
    entities = []
    for link_key, link_info in link_infos.items():
        if link_key.c_process is None or link_info.s_process is None:
            continue

        edge_attrs = []
        if link_info.link_metric:
            for m_key, m_val in asdict(link_info.link_metric).items():
                edge_attrs.append(Attr(key=m_key, value=m_val, vtype="string"))

        _anomaly_infos = []
        this_anomaly_infos = anomaly_infos.get(link_key, {}).get("anomaly_infos")
        if this_anomaly_infos:
            for i in this_anomaly_infos:
                _anomaly_infos.append(AnomalyInfo(anomaly_attr=i.get("anomaly_attr"),
                                                  anomaly_type=i.get("anomaly_type")))

        left_call = Call(type="PROCESS", id=link_info.c_node_id())
        right_call = Call(type="PROCESS", id=link_info.s_node_id())

        entity = Entity(entityid=link_info.link_id(),
                        type=link_info.link_type.upper(),
                        name=link_info.link_id(),
                        dependeditems=[Dependenceitem(calls=[left_call])],
                        dependingitems=[Dependenceitem(calls=[right_call])],
                        attrs=edge_attrs,
                        anomaly_infos=_anomaly_infos,
                        status=link_info.status)
        entities.append(entity)

    return entities


def get_lb_link_entities(lb_infos: Dict[LbLinkKey, LbLinkInfo]) -> List[Entity]:
    entities = []
    for lb_key, lb_info in lb_infos.items():
        if not lb_info.link_id():
            continue
        lb_attrs = []
        left_call = Call(type="PROCESS", id=lb_info.c_node_id())
        right_call = Call(type="PROCESS", id=lb_info.s_node_id())
        run_on = Runon(type="PROCESS", id=lb_info.lb_node_id())
        lb_attrs.append(Attr(key='example', value='0.1', vtype='float'))
        entity = Entity(entityid=lb_info.link_id(),
                        type=lb_info.link_type.upper(),
                        name=lb_info.link_id(),
                        dependeditems=[Dependenceitem(calls=[left_call])],
                        dependingitems=[Dependenceitem(calls=[right_call], run_ons=[run_on])])
        entities.append(entity)

    return entities


def get_process_node_entities(process_infos: Dict[str, ProcessNode]) -> List[Entity]:
    entities = []
    for proc_key, proc_info in process_infos.items():
        left_calls = []
        right_calls = []
        lb_runons = []
        node_attrs = []
        for l_edge in proc_info.l_edges:
            left_calls.append(Call(type=l_edge[1], id=l_edge[0]))
        for r_edge in proc_info.r_edges:
            right_calls.append(Call(type=r_edge[1], id=r_edge[0]))
        for lb_edge in proc_info.lb_edges:
            lb_runons.append(Runon(type=lb_edge[1], id=lb_edge[0]))
        on_runon = Runon(type="VM", id=proc_info.host.node_id())
        node_attrs.append(Attr(key='example', value="0xabcd", vtype="int"))
        entity = Entity(entityid=proc_key,
                        type="PROCESS",
                        name=proc_key,
                        dependeditems=[Dependenceitem(calls=left_calls, run_ons=lb_runons)],
                        dependingitems=[Dependenceitem(calls=right_calls, run_ons=[on_runon])],
                        attrs=node_attrs)
        entities.append(entity)

    return entities


def get_vm_node_entities(vm_infos: Dict[str, HostNode]) -> List[Entity]:
    entities = []
    for vm_key, vm_info in vm_infos.items():
        procs = []
        for proc in vm_info.processes:
            procs.append(Runon(type="PROCESS", id=proc))
        entity = Entity(entityid=vm_key,
                        type="VM",
                        name=vm_key,
                        dependeditems=[Dependenceitem(run_ons=procs)],
                        dependingitems=[Dependenceitem()])
        entities.append(entity)

    return entities


def get_observed_entity_list():  # noqa: E501
    """get observed entity list

    get observed entity list # noqa: E501

    :param timestamp: the time that cared
    :type timestamp: int

    :rtype: EntitiesResponse
    """
    entities = []
    # obtain tcp_link entities
    _edges_table, _proc_nodes_table, _lb_table, _vm_table = node_entity_process()
    if not _edges_table:
        clear_tmp()
        return 500

    detect_res = detection(_edges_table, _proc_nodes_table, _lb_table, _vm_table)
    edges_table, anomaly_table, proc_nodes_table, lb_table, vm_table = detect_res

    tcp_link_entities = get_tcp_link_entities(edges_table, anomaly_table)
    entities.extend(tcp_link_entities)

    lb_link_entities = get_lb_link_entities(lb_table)
    entities.extend(lb_link_entities)

    process_node_entities = get_process_node_entities(proc_nodes_table)
    entities.extend(process_node_entities)

    vm_node_entities = get_vm_node_entities(vm_table)
    entities.extend(vm_node_entities)

    if len(entities) == 0:
        code = 500
        msg = "Empty"
    else:
        code = 200
        msg = "Successful"

    entities_res = EntitiesResponse(code=code,
                                    msg=msg,
                                    timestamp=12345678,
                                    entities=entities)
    clear_tmp()
    return entities_res, 200


def get_topo_graph_status():  # noqa: E501
    """get Topo Graph Engine Service health status

    get Topo Graph Engine Service health status # noqa: E501


    :rtype: BaseResponse
    """

    clear_tmp()
    return 'clear tmp files!'


if __name__ == '__main__':
    #_edges_table, _proc_nodes_table, _lb_table, _vm_table = node_entity_process()
    # res = detection(_edges_table, _proc_nodes_table, _lb_table, _vm_table)
    # print(res[1])
    res = get_observed_entity_list()
    print(res)