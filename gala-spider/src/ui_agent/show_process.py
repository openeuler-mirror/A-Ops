from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import configparser
import time
import sys
sys.path.append("..")
#from data_process import ac
from data_process import edges_infos
from lib import util

# Color list (only 17 and please add if need..)
colors_list = ['black', 'red', 'green', 'blue', 'pink', 'brown', 'chocolate', 'yellow', 'violet',
               'powderblue', 'maroon', 'coral', 'darkgreen', 'cornsilk', 'cornflowerblue', 'darkblue']
# ner4j
def ui_neo4j_agent(n):
    # obtain temp_files & conf_file path
    (find_tcp_path, find_other_path, find_conf_path) = util.get_temp_file_path()
    # analysis configuration
    cf = configparser.ConfigParser()
    cf.read(find_conf_path[0], encoding="utf-8")
    graph_agent = cf.get("global", "ui_source")
    graph_addr = cf.get(eval(graph_agent), "address")
    graph_uname = cf.get(eval(graph_agent), "username")
    graph_pwd = cf.get(eval(graph_agent), "password")
    # connect to neo4j datebase
    graph = Graph(graph_addr, username=graph_uname, password=graph_pwd)
    # loop every n second
    while True:
        print("---------------------------")
        # clean graph
        graph.delete_all()
        # Obtain nodes and edges
        edges_table, edge_info = edges_infos.main()
        # Graph add node and edge
        for key in edges_table:
            matcher = NodeMatcher(graph)
            if len(edges_table[key]) == 2:
                #print(key, edges_table[key]['0'], edges_table[key]['1'])
                nodelist = list(matcher.match('elb', name=edges_table[key]['1']))
                if len(nodelist) > 0:
                    test_node_2=matcher.match("elb", name=edges_table[key]['1']).first()
                else:
                    test_node_2 = Node('elb', name=edges_table[key]['1'])
                    graph.create(test_node_2)
                nodelist = list(matcher.match('elb', name=edges_table[key]['0']))
                if len(nodelist) > 0:
                    test_node_3=matcher.match("elb", name=edges_table[key]['0']).first()
                else:
                    test_node_3 = Node('elb', name=edges_table[key]['0'])
                    graph.create(test_node_3)

                node_2_to_node_3 = Relationship(
                    test_node_2,
                    'link_count:%s tx_bytes:%s rx_bytes:%s' % (edge_info[key][7], edge_info[key][0], edge_info[key][1]),
                    test_node_3,
                    color=colors_list[0])
                rela_matcher = RelationshipMatcher(graph)
                res_list = list(rela_matcher.match({test_node_2, test_node_3}, color=colors_list[0]))
                if len(res_list) <= 0:
                    node_2_to_node_3['count'] = 1
                    graph.create(node_2_to_node_3)
                    print(node_2_to_node_3)
        # end of drawing, delete temporary files
        with open(find_tcp_path[0], 'wb') as file_t:
            file_t.truncate(0)
        with open(find_other_path[0], 'wb') as file_o:
            file_o.truncate(0)
        # run after time n
        time.sleep(n)


def main(ui_name, timer):
    if ui_name in ["neo4j"]:
        ui_neo4j_agent(timer)

#main("neo4j", 5)
