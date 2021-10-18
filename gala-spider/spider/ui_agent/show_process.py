from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import time
from spider.data_process.data_to_entity import node_entity_process
from spider.data_process.data_to_entity import clear_tmp
from spider.util.conf import neo4j_addr
from spider.util.conf import neo4j_uname
from spider.util.conf import neo4j_pwd

# Color list (Just list here...)
colors_list = ['black', 'red', 'green', 'blue', 'saddlebrown', 'brown', 'chocolate', 'yellow', 'violet',
               'powderblue', 'maroon', 'coral', 'lightgreen', 'ligntseagreen', 'limegreen', 'darkblue']
# ner4j
def ui_neo4j_agent(n):
    # connect to neo4j datebase
    graph = Graph(neo4j_addr, username=neo4j_uname, password=neo4j_pwd)
    # loop every n second
    while True:
        print("---------------------------")
        # clean graph
        graph.delete_all()
        # Obtain nodes and edges
        edges_table, edges_infos, nodes_table, lb_tables, vm_tables = node_entity_process()
        # Create node and tcp_link
        if edges_table is None:
            continue
        for key in edges_table:
            if len(edges_table[key]) < 2:
                continue
            matcher = NodeMatcher(graph)
            # src node
            nodelist = list(matcher.match('Process', name=edges_table[key]['src']))
            if len(nodelist) > 0:
                src_node = matcher.match("Process", name=edges_table[key]['src']).first()
            else:
                src_node = Node('Process',  name=edges_table[key]['src'], color='lightgreen', runon=edges_table[key]['1']['h'], type='Process')
                graph.create(src_node)
            # dst node
            nodelist = list(matcher.match('Process', name=edges_table[key]['dst']))
            if len(nodelist) > 0:
                dst_node = matcher.match("Process", name=edges_table[key]['dst']).first()
            else:
                dst_node = Node("Process", name=edges_table[key]['dst'], color='lightgreen', runon=edges_table[key]['0']['h'], type='Process')
                graph.create(dst_node)
            # tcp link
            tcp_link_relation = Relationship(
                src_node,
                'link_count:%s tx_bytes:%s rx_bytes:%s' % (edges_infos[key][7], edges_infos[key][0], edges_infos[key][1]),
                dst_node,
                type='TCP_LINK',
                color='black')
            rela_matcher = RelationshipMatcher(graph)
            res_list = list(rela_matcher.match({src_node, dst_node}, color='black'))
            if len(res_list) <= 0:
                tcp_link_relation['count'] = 1
                graph.create(tcp_link_relation)
        # Create lb_link
        if lb_tables is None:
            continue
        for key in lb_tables:
            matcher = NodeMatcher(graph)
            if len(lb_tables[key]) >= 5:
                c_node = matcher.match("Process", name=lb_tables[key]['src']).first()
                lb_node = matcher.match("Process", name=lb_tables[key]['lb']).first()
                s_node = matcher.match("Process", name=lb_tables[key]['dst']).first()
                lb_c_h_relation = Relationship(c_node, 'lb', lb_node, type=lb_tables[key]['tname'].upper(), color='yellow')
                graph.create(lb_c_h_relation)
                lb_h_s_relation = Relationship(lb_node, 'lb', s_node, type=lb_tables[key]['tname'].upper(), color='yellow')
                graph.create(lb_h_s_relation)
        # Create host_node
        if vm_tables is None:
            continue
        for key in vm_tables:
            if len(vm_tables[key]['proc']) < 1:
                continue
            matcher = NodeMatcher(graph)
            host = Node("Host", name=key, color='deepskyblue', runon='DateCenter', type='Host')
            for i in range(len(vm_tables[key]['proc'])):
                val = vm_tables[key]['proc'].pop()
                nodelist = list(matcher.match('Process', name=val))
                if len(nodelist) > 0:
                    proc = matcher.match("Process", name=val).first()
                    runon_relation = Relationship(
                        host,
                        'RUNON',
                        proc,
                        type='RUNON',
                        color='dodgerblue')
                    graph.create(runon_relation)

        clear_tmp()
        time.sleep(n)

#ui_neo4j_agent(50)
