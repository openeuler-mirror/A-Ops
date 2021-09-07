import os
import sys
import ast
import json
from spider.util.entityid import node_entity_name
from spider.util.entityid import edge_entity_name
from spider.util.conf import temp_tcp_file
from spider.util.conf import temp_other_file

def tcp_entity_process():
    s_nodes_table = {}
    c_edges_table = {}
    c_edges_infos = {}
    edges_table = {}
    edges_infos = {}
    if os.path.exists(ast.literal_eval(temp_tcp_file)):
        f = open(ast.literal_eval(temp_tcp_file))
    else:
        print("/var/tmp/spider/tcpline.txt not here.")
        sys.exit()
    lines = f.readline()
    while lines:
        # obtain label = hostname + process_name
        line_json = json.loads(lines)
        hostname = line_json.get("hostname")
        process_name = line_json.get("process_name")
        # obtain s_port + client_ip + server_ip
        s_port = line_json.get("server_port")
        c_ip = line_json.get("client_ip")
        s_ip = line_json.get("server_ip")
        if line_json.get("table_name") == "lvs_link":
            v_ip = line_json.get("virtual_ip")
            l_ip = line_json.get("local_ip")
            s_nodes_table.setdefault((v_ip, s_port), {}).setdefault('h', hostname)
            s_nodes_table.setdefault((v_ip, s_port), {}).setdefault('p', process_name)
            c_edges_table.setdefault((l_ip, s_ip, s_port), {}).setdefault('1', {}).setdefault('h', hostname)
            c_edges_table.setdefault((l_ip, s_ip, s_port), {}).setdefault('1', {}).setdefault('p', process_name)
        elif line_json.get("table_name") == "tcp_link" and c_ip != s_ip:
            role = line_json.get("role")
            if role == '0':
                s_nodes_table.setdefault((s_ip, s_port), {}).setdefault('h', hostname)
                s_nodes_table.setdefault((s_ip, s_port), {}).setdefault('p', process_name)
                c_edges_table.setdefault((c_ip, s_ip, s_port), {}).setdefault('0', {}).setdefault('h', hostname)
                c_edges_table.setdefault((c_ip, s_ip, s_port), {}).setdefault('0', {}).setdefault('p', process_name)
                c_edges_infos.setdefault((c_ip, s_ip, s_port),
                                         [line_json.get("tx_bytes"), line_json.get("rx_bytes"),
                                          line_json.get("packets_in"),
                                          line_json.get("packets_out"), line_json.get("retran_packets"),
                                          line_json.get("lost_packets"), line_json.get("rtt"),
                                          line_json.get("link_count")])
            elif role == '1':
                temp = hostname + '.' + process_name
                edges_table.setdefault((c_ip, s_ip, s_port, temp), {}).setdefault('1', {}).setdefault('h', hostname)
                edges_table.setdefault((c_ip, s_ip, s_port, temp), {}).setdefault('1', {}).setdefault('p', process_name)
                edges_infos.setdefault((c_ip, s_ip, s_port, temp),
                                       [line_json.get("rx_bytes"), line_json.get("tx_bytes"),
                                        line_json.get("packets_out"),
                                        line_json.get("packets_in"), line_json.get("retran_packets"),
                                        line_json.get("lost_packets"), line_json.get("rtt"),
                                        line_json.get("link_count")])
        lines = f.readline()

    for key in c_edges_table.keys():
        if c_edges_table[key].get('0') is not None and c_edges_table[key].get('1') is not None:
            temp = c_edges_table[key]['1']['h'] + '.' + c_edges_table[key]['1']['p']
            edges_table.setdefault((key[0], key[1], key[2], temp), c_edges_table[key])
            edges_infos.setdefault((key[0], key[1], key[2], temp), c_edges_infos[key])

    for key in edges_table.keys():
        node_key = (key[1], key[2])
        # fill edge_table '0' according to knowing nodes and lvs_edges
        if edges_table[key].get('0') is None and s_nodes_table.get(node_key) is not None:
            edges_table.setdefault(key, {}).setdefault('0', s_nodes_table[node_key])
    return edges_table, edges_infos


def lb_entity_process():
    lb_tables = {}
    if os.path.exists(ast.literal_eval(temp_other_file)):
        f = open(ast.literal_eval(temp_other_file))
    else:
        print("/var/tmp/spider/otherline.txt not here.")
        sys.exit()
    lines = f.readline()
    while lines:
        line_json = json.loads(lines)
        hostname = line_json.get("hostname")
        table_name = line_json.get("table_name")
        if table_name == "dnsmasq_link":
            s_port = "8888"                             # dnsmasq探针没有回传dns的port
            #lb_tables.setdefault((hostname, process_name), {}).setdefault("c-v", (c_ip, v_ip, s_port))
        else:
            c_ip = line_json.get("client_ip")
            v_ip = line_json.get("virtual_ip")
            s_ip = line_json.get("server_ip")
            s_port = line_json.get("server_port")
            if table_name == "nginx_statistic":
                process_name = "nginx"
                lb_tables.setdefault((hostname, process_name), {}).setdefault("c-v", (c_ip, v_ip, s_port))
                lb_tables.setdefault((hostname, process_name), {}).setdefault("v-s", (v_ip, s_ip, s_port))
            elif table_name == "haproxy_link":
                process_name = "haproxy"
                lb_tables.setdefault((hostname, process_name), {}).setdefault("c-v", (c_ip, v_ip, s_port))
                lb_tables.setdefault((hostname, process_name), {}).setdefault("v-s", (v_ip, s_ip, s_port))
        lines = f.readline()
    return lb_tables


def node_entity_process():
    nodes_table = {}
    edges_table, edges_infos = tcp_entity_process()
    lb_tables = lb_entity_process()
    for key in edges_table.keys():
        if len(edges_table[key]) == 2:
            dst_node_id = node_entity_name(edges_table[key]['0']['h'], edges_table[key]['0']['p'], None)
            src_node_id = node_entity_name(edges_table[key]['1']['h'], edges_table[key]['1']['p'], None)
            edge_id = edge_entity_name("tcp_link", edges_table[key]['0']['h'], edges_table[key]['0']['p'],
                                       edges_table[key]['1']['h'], edges_table[key]['1']['p'])
            edges_table.setdefault(key, {}).setdefault('src', src_node_id)
            edges_table.setdefault(key, {}).setdefault('dst', dst_node_id)
            edges_table.setdefault(key, {}).setdefault('edge', edge_id)
            print("tcp---", key, edges_table[key])
            nodes_table.setdefault(src_node_id, {}).setdefault('host', edges_table[key]['1']['h'])
            nodes_table.setdefault(src_node_id, {}).setdefault('r_edge', [])
            nodes_table[src_node_id].get('r_edge').append((edge_id, "TCP_LINK"))
            nodes_table.setdefault(dst_node_id, {}).setdefault('host', edges_table[key]['0']['h'])
            nodes_table.setdefault(dst_node_id, {}).setdefault('l_edge', [])
            nodes_table[dst_node_id].get('l_edge').append((edge_id, "TCP_LINK"))
            for lb_key in lb_tables.keys():
                if lb_tables[lb_key]['c-v'][0] == key[0] and \
                                lb_tables[lb_key]['c-v'][1] == key[1] and \
                                lb_tables[lb_key]['c-v'][2] == key[2]:
                    lb_tables.setdefault(lb_key, {}).setdefault('src', src_node_id)
                if lb_tables[lb_key]['v-s'][0] == key[0] and \
                                lb_tables[lb_key]['v-s'][1] == key[1] and \
                                lb_tables[lb_key]['v-s'][2] == key[2]:
                    lb_tables.setdefault(lb_key, {}).setdefault('dst', dst_node_id)

    for key in lb_tables.keys():
        print("lb----", key, lb_tables[key])
        lb_node_id = node_entity_name(key[0], key[1], None)
        lb_tables.setdefault(key, {}).setdefault('on', lb_node_id)
        if key[1] == "dnsmasq":
            type = "DNSMASQ-LINK"
        elif key[1] == "nginx":
            type = "NGINX-LINK"
            lb_id = edge_entity_name("nginx_link", None, lb_tables[key]['dst'], None, lb_tables[key]['src'])
            lb_tables.setdefault(key, {}).setdefault("lb_id", lb_id)
        elif key[1] == "haproxy":
            lb_id = edge_entity_name("haproxy_link", None, lb_tables[key]['dst'], None, lb_tables[key]['src'])
            lb_tables.setdefault(key, {}).setdefault("lb_id", lb_id)

        nodes_table.setdefault(lb_node_id, {}).setdefault('lb_edge', [])
        nodes_table[lb_node_id].get('lb_edge').append((lb_tables[key]['lb_id'], type))

    for key in nodes_table.keys():
        print("node----", key, nodes_table[key])

    return edges_table, edges_infos, nodes_table, lb_tables


def clear_tmp():
    with open(ast.literal_eval(temp_tcp_file), 'wb') as file_t:
        file_t.truncate(0)
    with open(ast.literal_eval(temp_other_file), 'wb') as file_o:
        file_o.truncate(0)