from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import time
from spider.data_process.data_to_entity import node_entity_process
from spider.data_process.data_to_entity import clear_tmp
from spider.util.conf import neo4j_addr
from spider.util.conf import neo4j_uname
from spider.util.conf import neo4j_pwd
from spider.controllers.gala_spider import get_observed_entity_list

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
        res, code = get_observed_entity_list()
        if res.code != 200:
            continue

        entities_list = res.entities
        for i in range(len(entities_list)):
            entity = entities_list[i]
            # Create node and tcp_link
            if entity.type == 'TCP-LINK':
                matcher = NodeMatcher(graph)
                # src_node
                nodelist = list(matcher.match('Process', name=entity.dependeditems.calls.id))
                if len(nodelist) > 0:
                    src_node = matcher.match('Process', name=entity.dependeditems.calls.id).first()
                else:
                    src_node = Node('Process', name=entity.dependeditems.calls.id, color='lightgreen', type='Process')
                    graph.create(src_node)
                # dst_node
                nodelist = list(matcher.match('Process', name=entity.dependingitems.calls.id))
                if len(nodelist) > 0:
                    dst_node = matcher.match("Process", name=entity.dependingitems.calls.id).first()
                else:
                    dst_node = Node('Process', name=entity.dependingitems.calls.id, color='lightgreen', type='Process')
                    graph.create(dst_node)

                # tcp_link颜色：缺失->blue, 存在且无异常->black, 存在且有异常->red,
                _color = 'black'
                if entity.status == 0:
                    _color = "blue"
                elif len(entity.anomaly_infos) > 0:
                    _color = "red"

                # link标签
                _description = "- - -" if len(entity.attrs) == 0 else "link_count:{} retran_packets:{} lost_packets:{}".\
                    format(entity.attrs[0].value, entity.attrs[5].value, entity.attrs[6].value)

                # tcp_link
                tcp_link_relation = Relationship(
                    src_node,
                    _description,
                    dst_node,
                    type = 'TCP_LINK',
                    color = _color)
                tcp_link_relation['count'] = 1
                graph.create(tcp_link_relation)
            elif entity.type == 'PROCESS':
                continue
            # Create host_node
            elif entity.type == 'VM':
                matcher = NodeMatcher(graph)
                host = Node("Host", name=entity.name, color='deepskyblue', runon='DateCenter', type='Host')
                for i in range(len(entity.dependeditems.run_ons)):
                    nodelist = list(matcher.match('Process', name=entity.dependeditems.run_ons[i].id))
                    if len(nodelist) > 0:
                        proc = matcher.match("Process", name=entity.dependeditems.run_ons[i].id).first()
                        runon_relation = Relationship(
                            host,
                            'RUNON',
                            proc,
                            type='RUNON',
                            color='dodgerblue')
                        graph.create(runon_relation)
            else:
                # Create lb_link
                matcher = NodeMatcher(graph)
                c_node = matcher.match("Process", name=entity.dependeditems.calls.id).first()
                lb_node = matcher.match("Process", name=entity.dependingitems.run_ons.id).first()
                s_node = matcher.match("Process", name=entity.dependingitems.calls.id).first()
                lb_c_h_relation = Relationship(c_node, 'lb', lb_node, type=entity.type, dst=entity.dependingitems.calls.id, color='yellow')
                graph.create(lb_c_h_relation)
                lb_h_s_relation = Relationship(lb_node, 'lb', s_node, type=entity.type, src=entity.dependeditems.calls.id, color='yellow')
                graph.create(lb_h_s_relation)

        clear_tmp()
        time.sleep(n)

#ui_neo4j_agent(50)
