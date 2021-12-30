from typing import Dict
from spider.data_process.models import TcpLinkKey, TcpLinkInfo
from anomaly_detection.util import g_edges_list, EDGES_LIST_UPDATE_INTERVAL, EntityName

def update_edges_info(edges_table: Dict[TcpLinkKey, TcpLinkInfo], timestamp):
    """
    update tcp_link baseline
    :param edges_table: link info
    :param timestamp: data collection time
    """
    edges_list = {}
    for edge, edge_info in edges_table.items():
        if edge_info.s_process and edge_info.key.c_process:
            edges_list[edge] = edge_info

    g_edges_list[EntityName.TCP_LINK] = edges_list
    g_edges_list["timestamp"] = timestamp
    return


def tcp_link_item_detection(tcp_link_items, timestamp):
    """
    Check whether the tcp_link is missing.
    """
    if not tcp_link_items or not timestamp:
        print("tcp_link_item_detection error 1")
        return tcp_link_items

    # status: [1:normal, 0:missing]
    for tcp_link in tcp_link_items:
        tcp_link_items[tcp_link].status = 1

    g_edges_list_timestamp = g_edges_list.get("timestamp")
    if (int(timestamp) - int(g_edges_list_timestamp)) >= EDGES_LIST_UPDATE_INTERVAL:
        update_edges_info(tcp_link_items, timestamp)
        return tcp_link_items

    _edges_list = [edge for edge in tcp_link_items.keys()]
    for edge in g_edges_list.get(EntityName.TCP_LINK, {}).keys():
        if edge not in _edges_list:
            tcp_link_items[edge] = g_edges_list.get(EntityName.TCP_LINK, {}).get(edge)
            tcp_link_items[edge].status = 0

    return tcp_link_items


def node_item_detection(node_items, timestamp):
    return node_items


def lb_item_detection(lb_items, timestamp):
    return lb_items


def vm_item_detection(vm_items, timestamp):
    return vm_items