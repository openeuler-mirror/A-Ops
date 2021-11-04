import os
import json
import ast

from typing import Dict

from spider.util.conf import temp_tcp_file
from spider.util.conf import temp_other_file
from spider.util.conf import exclude_ip
from spider.data_process.models import HostNode, ProcessNode
from spider.data_process.models import TcpLinkKey, TcpLinkInfo, TcpLinkMetric
from spider.data_process.models import LbLinkKey, LbLinkInfo


def tcp_entity_process() -> Dict[TcpLinkKey, TcpLinkInfo]:
    linkinfos = {}
    process_infos = {}

    if not os.path.exists(temp_tcp_file):
        print("{} not exist.".format(temp_tcp_file))
        return {}

    with open(temp_tcp_file) as f:
        for line in f:
            line_json = json.loads(line)
            if line_json.get('client_ip') in ast.literal_eval(exclude_ip):
                continue
            if line_json.get('server_ip') in ast.literal_eval(exclude_ip):
                continue

            table_name = line_json.get('table_name')
            hostname = line_json.get('hostname')
            process_name = line_json.get('process_name')
            s_ip = line_json.get('server_ip')
            s_port = line_json.get('server_port')
            c_ip = line_json.get('client_ip')
            process = ProcessNode(HostNode(hostname), process_name)

            if table_name == 'tcp_link':
                if s_ip == c_ip:
                    continue
                role = line_json.get('role')
                linkmetric = TcpLinkMetric(line_json.get('rx_bytes', ''),
                                           line_json.get('tx_bytes', ''),
                                           line_json.get('packets_out', ''),
                                           line_json.get('packets_in', ''),
                                           line_json.get('retran_packets', ''),
                                           line_json.get('lost_packets', ''),
                                           line_json.get('rtt', ''),
                                           line_json.get('link_count', ''))
                c_process = None
                if role == '0':
                    process_infos[(s_ip, s_port)] = process
                elif role == '1':
                    c_process = process

                key = TcpLinkKey(s_ip, s_port, c_ip, c_process)
                linkinfos.setdefault(key, TcpLinkInfo(key))
                linkinfos[key].link_metric = linkmetric
            elif table_name == 'ipvs_link':
                v_ip = line_json.get('virtual_ip')
                v_port = line_json.get('virtual_port')
                l_ip = line_json.get('local_ip')

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


def lb_entity_process() -> Dict[LbLinkKey, LbLinkInfo]:
    lb_tables = {}
    if not os.path.exists(temp_other_file):
        print("{} not exist".format(temp_other_file))
        return {}

    with open(temp_other_file) as f:
        for line in f:
            line_json = json.loads(line)
            hostname = line_json.get("hostname")
            table_name = line_json.get("table_name")
            process_name = line_json.get("process_name")
            if not process_name:
                process_name = table_name.split("_")[0]
            process = ProcessNode(HostNode(hostname), process_name)

            if table_name == "dnsmasq_link":
                pass
            else:
                s_ip = line_json.get("server_ip")
                s_port = line_json.get("server_port")
                v_ip = line_json.get("virtual_ip")
                v_port = line_json.get("virtual_port")
                c_ip = line_json.get("client_ip")
                if table_name == "ipvs_link":
                    l_ip = line_json.get("local_ip")
                else:
                    l_ip = v_ip

                key = LbLinkKey(s_ip, s_port, v_ip, v_port, l_ip, c_ip)
                lb_info = LbLinkInfo(key, lb_process=process, link_type=table_name)
                lb_tables.setdefault(key, lb_info)

    return lb_tables


def node_entity_process() -> tuple:
    node_infos = {}
    vm_infos = {}

    link_infos = tcp_entity_process()
    if len(link_infos) == 0:
        print("Please wait kafka consumer datas...")
        return None, None, None, None
    lb_infos = lb_entity_process()

    for key, linkinfo in link_infos.items():
        if linkinfo.s_process is None or linkinfo.key.c_process is None:
            continue

        dst_node_id = linkinfo.s_node_id()
        src_node_id = linkinfo.c_node_id()
        link_id = linkinfo.link_id()

        node_infos.setdefault(src_node_id, linkinfo.key.c_process)
        linkinfo.key.c_process.r_edges.append((link_id, linkinfo.link_type.upper()))
        node_infos.setdefault(dst_node_id, linkinfo.s_process)
        linkinfo.s_process.l_edges.append((link_id, linkinfo.link_type.upper()))

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
            lbinfo.lb_process.lb_edges.append((lbinfo.link_id(), lbinfo.link_type.upper()))

    for node_id, process_info in node_infos.items():
        if len(process_info.r_edges) == 0 and len(process_info.l_edges) == 0:
            print(node_id, "only lb link and no tcplink, please check...")
            continue
        vm_infos.setdefault(process_info.host.node_id(), process_info.host)
        process_info.host.processes.append(process_info.node_id())

    return link_infos, node_infos, lb_infos, vm_infos


def clear_tmp():
    with open(temp_tcp_file, 'wb') as file_t:
        file_t.truncate(0)
    with open(temp_other_file, 'wb') as file_o:
        file_o.truncate(0)


if __name__ == '__main__':
    print(node_entity_process())
