import json
import sys
sys.path.append("..")
from lib import util

def main():
    nodes_table = {}
    edges_table = {}
    edges_infos = {}
    lbedges_table = {}
    # Obtain temp_file's path
    (find_tcp_files, NULL, NULL) = util.get_temp_file_path()
    f = open(find_tcp_files[0])
    lines = f.readline()
    while lines:
        # obtain label = host + procname
        line_json = json.loads(lines)
        host = line_json.get("host")
        procname = line_json.get("procname")
        # obtain s_port + client_ip + server_ip
        s_port = line_json.get("s_port")
        c_ip = line_json.get("client_ip")
        s_ip = line_json.get("server_ip")
        if procname in ["sshd", "rdk:broker0"]:
            lines = f.readline()
            continue
        if line_json.get("table_name") == "lvs_link":
	    v_ip = line_json.get("virtual_ip")
	    l_ip = line_json.get("local_ip")
            lbedges_table.setdefault((c_ip, v_ip, s_port), {}).setdefault('0', host + '.' + procname)
            lbedges_table.setdefault((l_ip, s_ip, s_port), {}).setdefault('1', host + '.' + procname)
        if line_json.get("table_name") == "tcp_link" and c_ip != s_ip:
            if line_json.get("role") == '0':
                nodes_table.setdefault((s_ip, s_port), host + '.' + procname)
            edges_table.setdefault((c_ip, s_ip, s_port), {}).setdefault(line_json.get("role"), host + '.' + procname)
            edges_infos.setdefault((c_ip, s_ip, s_port), [line_json.get("tx_bytes"), line_json.get("rx_bytes"),
                                   line_json.get("packets_in"), line_json.get("packets_out"), 
                                   line_json.get("retran_packets"), line_json.get("lost_packets"), line_json.get("rtt"),
                                   line_json.get("link_count")])
        lines = f.readline()

    for key in edges_table.keys():
        node_key = (key[1], key[2])
        # fill edge_table according to knowing nodes
        if edges_table[key].get('0') is None and nodes_table.get(node_key) is not None:
            edges_table.setdefault(key, {}).setdefault('0', nodes_table[node_key])
        # fill edge_table according to lvs_table
        if lbedges_table.get(key) is not None:
            if edges_table[key].get('0') is None:
                edges_table.setdefault(key, {}).setdefault('0', lbedges_table[key]['0'])
            if edges_table[key].get('1') is None:
                edges_table.setdefault(key, {}).setdefault('1', lbedges_table[key]['1'])
        #print(key, edges_table[key])

    return edges_table, edges_infos

#main()

