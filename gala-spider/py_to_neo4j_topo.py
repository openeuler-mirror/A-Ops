from matplotlib.font_manager import FontProperties
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import edge_generate as base_info
import kafka_zyx as kafka_consumer
import time
import configparser
import multiprocessing

# Delete tcpline.txt & otherline.txt after draw topo
def delfile():
    with open("tcpline.txt", 'wb') as file_t:
        file_t.truncate(0)
    with open("otherline.txt", 'wb') as file_o:
        file_o.truncate(0)

# run every n second
def timer(n):
    # analysis configuration
    cf = configparser.ConfigParser()
    cf.read("gala-spider.conf", encoding="utf-8")
    graph_agent = cf.get("global", "ui_source")
    graph_addr = cf.get(eval(graph_agent), "address")
    graph_uname = cf.get(eval(graph_agent), "username")
    graph_pwd = cf.get(eval(graph_agent), "password")

    if eval(graph_agent) == "neo4j":
        # connect to neo4j datebase
        graph = Graph(graph_addr, username=graph_uname, password=graph_pwd)

    while True:
        # clean graph
        graph.delete_all()

        # Obtain nodes and edges
        nodes, edges = base_info.main()
        print(edges)

        # Color list (only 17 and please add if need..)
        colors_list = ['whitesmoke', 'red', 'green', 'blue', 'black', 'brown', 'chocolate', 'yellow', 'violet',
                       'powderblue', 'maroon', 'coral', 'darkgreen', 'cornsilk', 'cornflowerblue', 'darkblue']

        # Graph add node and edge
        for num in range(len(edges)):
            matcher = NodeMatcher(graph)
            nodelist = list(matcher.match('elb', name=edges[num][5]))
            if len(nodelist) > 0:
                test_node_2=matcher.match("elb", name=edges[num][5]).first()
            else:
                test_node_2 = Node('elb', name=edges[num][5], id=edges[num][2], key=edges[num][0])
                graph.create(test_node_2)
            nodelist = list(matcher.match('elb', name=edges[num][6]))
            if len(nodelist) > 0:
                test_node_3=matcher.match("elb", name=edges[num][6]).first()
            else:
                test_node_3 = Node('elb', name=edges[num][6], id=edges[num][3], key=edges[num][1])
                graph.create(test_node_3)
            if int(edges[num][8]) >= 0:
                node_2_to_node_3 = Relationship(test_node_2, 'link_count:%s tx_bytes:%s rx_bytes:%s' % (
                    edges[num][14], edges[num][7], edges[num][8]), test_node_3, color=colors_list[edges[num][4]])
                node_2_to_node_3['count'] = 1
                rela_matcher = RelationshipMatcher(graph)
                res_list = list(rela_matcher.match({test_node_2, test_node_3}, color=colors_list[edges[num][4]]))
                if len(res_list) <= 0:
                    graph.create(node_2_to_node_3)
                    print(node_2_to_node_3)

        # end of drawing, delete temporary files
        delfile()

        time.sleep(n)

if __name__ == '__main__':
    # Multi-process
    record = []
    process = multiprocessing.Process(target=kafka_consumer.main)
    process.start()
    record.append(process)
    process = multiprocessing.Process(target=timer, args=(5,))
    process.start()
    record.append(process)
    for process in record:
        process.join()
