import json

from typing import Dict, List

from spider.util.conf import temp_tcp_file
from spider.util.conf import temp_other_file
from spider.util.conf import exclude_ip
from spider.util.conf import other_table
from spider.util.conf import db_agent
from spider.data_process.models import HostNode, ProcessNode
from spider.data_process.models import TcpLinkKey, TcpLinkInfo, TcpLinkMetric
from spider.data_process.models import LbLinkKey, LbLinkInfo
from spider.data_process.prometheus_process import g_prometheus_processor


def get_entities_from_kafka() -> List[dict]:
    res = []

    try:
        with open(temp_tcp_file) as f:
            for line in f:
                res.append(dict(json.loads(line)))

        with open(temp_other_file) as f:
            for line in f:
                res.append(dict(json.loads(line)))
    except IOError as ex:
        print(ex)

    return res


def tcp_entity_process(entities: List[dict]) -> Dict[TcpLinkKey, TcpLinkInfo]:
    linkinfos = {}
    process_infos = {}

    for entity in entities:
        if entity.get('client_ip') in exclude_ip:
            continue
        if entity.get('server_ip') in exclude_ip:
            continue

        table_name = entity.get('table_name')
        hostname = entity.get('hostname')
        process_name = entity.get('process_name')
        s_ip = entity.get('server_ip')
        s_port = entity.get('server_port')
        c_ip = entity.get('client_ip')
        if not s_ip or not s_port or not c_ip or not hostname or not process_name:
            continue
        process = ProcessNode(HostNode(hostname), process_name)

        if table_name == 'tcp_link':
            if s_ip == c_ip:
                continue
            role = entity.get('role')
            linkmetric = TcpLinkMetric(entity.get('rx_bytes', ''),
                                       entity.get('tx_bytes', ''),
                                       entity.get('packets_out', ''),
                                       entity.get('packets_in', ''),
                                       entity.get('retran_packets', ''),
                                       entity.get('lost_packets', ''),
                                       entity.get('rtt', ''),
                                       entity.get('link_count', ''))
            c_process = None
            if role == '0':
                process_infos[(s_ip, s_port)] = process
            elif role == '1':
                c_process = process

            key = TcpLinkKey(s_ip, s_port, c_ip, c_process)
            linkinfos.setdefault(key, TcpLinkInfo(key))
            linkinfos[key].link_metric = linkmetric
        elif table_name == 'ipvs_link':
            v_ip = entity.get('virtual_ip')
            v_port = entity.get('virtual_port')
            l_ip = entity.get('local_ip')
            if not v_ip or not v_port or not l_ip:
                continue

            process_infos[(v_ip, v_port)] = process

            key = TcpLinkKey(s_ip, s_port, l_ip, process)
            linkinfos.setdefault(key, TcpLinkInfo(key))

    for key, linkinfo in linkinfos.items():
        if key.c_process is None:
            continue

        linkinfo.link_type = "tcp_link"

        # ipvs link client side use the metric of it's server side
        tmp_key = TcpLinkKey(key.s_ip, key.s_port, key.c_ip, None)
        if tmp_key in linkinfos and linkinfo.link_metric is None:
            linkinfo.link_metric = linkinfos[tmp_key].link_metric

        if linkinfo.s_process is None and (key.s_ip, key.s_port) in process_infos:
            linkinfo.s_process = process_infos[(key.s_ip, key.s_port)]

    res = {}
    for key in linkinfos:
        if key.c_process is not None:
            res[key] = linkinfos.get(key)

    return res


def lb_entity_process(entities: List[dict]) -> Dict[LbLinkKey, LbLinkInfo]:
    lb_tables = {}

    for entity in entities:
        table_name = entity.get("table_name")
        if table_name not in other_table:
            continue
        hostname = entity.get("hostname")
        process_name = entity.get("process_name")
        if not process_name:
            process_name = table_name.split("_")[0]
        if not hostname or not process_name:
            continue
        process = ProcessNode(HostNode(hostname), process_name)

        if table_name == "dnsmasq_link":
            pass
        else:
            s_ip = entity.get("server_ip")
            s_port = entity.get("server_port")
            v_ip = entity.get("virtual_ip")
            v_port = entity.get("virtual_port")
            c_ip = entity.get("client_ip")
            if table_name == "ipvs_link":
                l_ip = entity.get("local_ip")
            else:
                l_ip = v_ip
            if not s_ip or not s_port or not v_ip or not v_port or not l_ip or not c_ip:
                continue

            key = LbLinkKey(s_ip, s_port, v_ip, v_port, l_ip, c_ip)
            lb_info = LbLinkInfo(key, lb_process=process, link_type=table_name)
            lb_tables.setdefault(key, lb_info)

    return lb_tables


def get_observe_entities() -> List[dict]:
    entities = []
    _db_agent = db_agent

    if _db_agent == "prometheus":
        entities = g_prometheus_processor.get_observe_entities()
    elif _db_agent == "kafka":
        entities = get_entities_from_kafka()
    else:
        print("Unknown data source:{}, please check!".format(_db_agent))

    return entities


def node_entity_process() -> tuple:
    node_infos = {}
    vm_infos = {}

    entities = get_observe_entities()

    link_infos = tcp_entity_process(entities)
    if len(link_infos) == 0:
        print("No data arrived, please wait...")
        return None, None, None, None
    lb_infos = lb_entity_process(entities)

    for key, linkinfo in link_infos.items():
        if linkinfo.s_process is None or linkinfo.key.c_process is None:
            continue

        dst_node_id = linkinfo.s_node_id()
        src_node_id = linkinfo.c_node_id()
        link_id = linkinfo.link_id()

        node_infos.setdefault(src_node_id, linkinfo.key.c_process)
        node_infos.get(src_node_id).r_edges.append((link_id, linkinfo.link_type.upper()))
        node_infos.setdefault(dst_node_id, linkinfo.s_process)
        node_infos.get(dst_node_id).l_edges.append((link_id, linkinfo.link_type.upper()))

        for lb_key, lbinfo in lb_infos.items():
            if lb_key.c_ip == key.c_ip and lb_key.v_ip == key.s_ip and \
                    lb_key.v_port == key.s_port:
                lbinfo.c_process = linkinfo.key.c_process
            if lb_key.l_ip == key.c_ip and lb_key.s_ip == key.s_ip and \
                    lb_key.s_port == key.s_port:
                lbinfo.s_process = linkinfo.s_process

    for lb_key, lbinfo in lb_infos.items():
        if lbinfo.lb_process is None:
            continue
        lb_node_id = lbinfo.lb_node_id()

        if lbinfo.link_type == 'dnsmasq_link':
            continue
        else:
            node_infos.setdefault(lb_node_id, lbinfo.lb_process)
            node_infos.get(lb_node_id).lb_edges.append((lbinfo.link_id(), lbinfo.link_type.upper()))

    for node_id, process_info in node_infos.items():
        if len(process_info.r_edges) == 0 and len(process_info.l_edges) == 0:
            print(node_id, "only lb link and no tcplink, please check...")
            continue
        vm_infos.setdefault(process_info.host.node_id(), process_info.host)
        vm_infos.get(process_info.host.node_id()).processes.append(process_info.node_id())

    return link_infos, node_infos, lb_infos, vm_infos


def clear_tmp():
    with open(temp_tcp_file, 'wb') as file_t:
        file_t.truncate(0)
    with open(temp_other_file, 'wb') as file_o:
        file_o.truncate(0)


if __name__ == '__main__':
    print(node_entity_process())
