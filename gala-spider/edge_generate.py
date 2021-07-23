from kafka import KafkaConsumer
import json
import itertools
import node_generate as node

# Get id + node for start&end nodes in edge table, according to node list
def obtain_node_add_id(nodes, ip, port):
    for i in nodes:
        if ip == i[3] and port == i[4]:
            return i[0], i[1], i[2]
    return -1, -1, -1

# Obtain relationship from otherline.txt, to determine edge's color
def obtain_relation_info(nodes):
    relation_set = set()
    o = open("otherline.txt")
    lines = o.readline()
    while lines:
        line_json = json.loads(lines)
        table_name = line_json.get("table_name")
        (c_id, c_node, temp) = obtain_node_add_id(nodes, line_json.get("client_ip"), line_json.get("server_port"))
        (v_id, v_node, temp) = obtain_node_add_id(nodes, line_json.get("virtual_ip"), line_json.get("server_port"))
        (r_id, r_node, temp) = obtain_node_add_id(nodes, line_json.get("server_ip"), line_json.get("server_port"))
        if table_name == "lvs_link":
            (l_id, l_node, temp) = obtain_node_add_id(nodes, line_json.get("local_ip"), line_json.get("server_port"))
            relation_set.add(((c_id, v_id), (v_id, l_id), (l_id, r_id)))
        elif table_name == "nginx_statistic" or table_name == "haproxy_link":
            relation_set.add(((c_id, v_id), (v_id, r_id)))
        else:
            lines = o.readline()
            continue
        lines = o.readline()
    # Color table
    colornum = range(1, len(relation_set) + 1)
    relation_list = list(relation_set)
    color_list = list(colornum)
    for i in range(len(relation_list) - 1):
        for j in range(i + 1, len(relation_list)):
            i_end = len(relation_list[i]) - 1
            j_len = len(relation_list[j]) - 1
            # if i_start == j_end || j_start == i_start
            if relation_list[i][0] == relation_list[j][j_len] or relation_list[i][i_end] == relation_list[j][0]:
                color_list[j] = color_list[i]
    return relation_list, color_list

# Determine color number according to relationship table
def obtain_color(nodes, source_id, target_id):
    edges_relation_list, color_list = obtain_relation_info(nodes)
    for i in range(len(edges_relation_list)):
        if (source_id, target_id) in edges_relation_list[i]:
            return color_list[i]
    return -1


def main():
    # Obtain nodes table
    nodes = node.main()
    # Obtain edge_full line's info: source_key_id->target_ke_id
    edge_full = set()
    i = -1
    f = open("tcpline.txt")
    lines = f.readline()
    while lines:
        # Obtain line's info[source_id target_id target_port]
        line_json = json.loads(lines)
        server_port = line_json.get("server_port")
        if line_json.get('role'):
            # if tcp_link, client_ip -> server_ip
            (source_id, source_node, s_name) = obtain_node_add_id(nodes, line_json.get("client_ip"), server_port)
            (target_id, target_node, t_name) = obtain_node_add_id(nodes, line_json.get("server_ip"), server_port)
            coler_num = obtain_color(nodes, source_id, target_id)
            if target_id != -1 and source_id != -1:
                tx_bytes = line_json.get("tx_bytes")
                rx_bytes = line_json.get("rx_bytes")
                packets_in = line_json.get("packets_in")
                packets_out = line_json.get("packets_out")
                retran_packets = line_json.get("retran_packets")
                lost_packets = line_json.get("lost_packets")
                rtt = line_json.get("rtt")
                link_count = line_json.get("link_count")
                edge_full.add((source_id, target_id, source_node, target_node, coler_num, s_name, t_name,
                                  tx_bytes, rx_bytes, packets_in, packets_out, retran_packets, lost_packets,
				  rtt, link_count))
        else:
            # if ipvs_link, cip->vip && vip->lip && lip->rip
            (c_id, c_node, c_name) = obtain_node_add_id(nodes, line_json.get("virtual_ip"), server_port)
            (v_id, v_node, v_name) = obtain_node_add_id(nodes, line_json.get("server_ip"), server_port)
            (l_id, l_node, l_name) = obtain_node_add_id(nodes, line_json.get("local_ip"), server_port)
            coler_num = obtain_color(nodes, c_id, l_id)
            if c_id != -1 and v_id != -1 and coler_num != -1:
                edge_full.add((c_id, v_id, c_node, v_node, coler_num, c_name, v_name, 0, i))
                i = i - 1
        lines = f.readline()
    #print(list(edge_full))
    return nodes, list(edge_full)

if __name__ == '__main__':
    main()

