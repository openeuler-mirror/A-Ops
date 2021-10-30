from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import time
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
            print("get_observed_entity_list get None")
            time.sleep(n)
            continue
        entities_list = res.entities
        for i in range(len(entities_list)):
            entity = entities_list[i]
            # Create node and tcp_link
            if entity.type == 'TCP_LINK':
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
                # tcp_link color: link missing->blue, attribute normal->black, attribue abnormal->red.
                _color = 'black'
                if entity.status == 0:
                    _color = "blue"
                elif len(entity.anomaly_infos) > 0:
                    _color = "red"
                # link lable
                _description = "- - -" if len(entity.attrs) == 0 else "link_count:{} retran_packets:{} lost_packets:{}".\
                    format(entity.attrs[0].value, entity.attrs[5].value, entity.attrs[6].value)
                # tcp_link
                tcp_link_relation = Relationship(
                    src_node,
                    _description,
                    dst_node,
                    type = 'TCP_LINK',
                    color = _color)
                print("neo4j:", tcp_link_relation)
                tcp_link_relation['count'] = 1
                graph.create(tcp_link_relation)
            elif entity.type == 'PROCESS':
                continue
            # Create host_node
            elif entity.type == 'VM':
                matcher = NodeMatcher(graph)
                host = Node("Host", name=entity.name, color='deepskyblue', runon='DateCenter', type='Host')
                for j in range(len(entity.dependeditems.run_ons)):
                    nodelist = list(matcher.match('Process', name=entity.dependeditems.run_ons[j].id))
                    if len(nodelist) > 0:
                        proc = matcher.match("Process", name=entity.dependeditems.run_ons[j].id).first()
                        runon_relation = Relationship(
                            host,
                            'RUNON',
                            proc,
                            type='RUNON',
                            color='dodgerblue')
                        print("neo4j:", tcp_link_relation)
                        graph.create(runon_relation)
            else:
                # Create lb_link
                matcher = NodeMatcher(graph)
                c_node = matcher.match("Process", name=entity.dependeditems.calls.id).first()
                lb_node = matcher.match("Process", name=entity.dependingitems.run_ons.id).first()
                s_node = matcher.match("Process", name=entity.dependingitems.calls.id).first()
                dst_id = entity.dependingitems.calls.id
                lb_c_h_relation = Relationship(c_node, 'lb', lb_node, type=entity.type, dst=dst_id, color='yellow')
                print("neo4j:", lb_c_h_relation)
                graph.create(lb_c_h_relation)
                src_id = entity.dependeditems.calls.id
                lb_h_s_relation = Relationship(lb_node, 'lb', s_node, type=entity.type, src=src_id, color='yellow')
                print("neo4j:", lb_h_s_relation)
                graph.create(lb_h_s_relation)

        time.sleep(n)

#ui_neo4j_agent(50)
