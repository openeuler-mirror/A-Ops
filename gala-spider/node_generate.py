from kafka import KafkaConsumer
import json

def main():
    node_full = set()
    f = open("tcpline.txt")
    lines = f.readline()
    while lines:
        # obtain label = hostname+process_name
        line_json = json.loads(lines)
        hostname = line_json.get("hostname")
        process_name = line_json.get("process_name")
        # obtain server_port
        server_port = line_json.get("server_port")
        if line_json.get("role"):
            # if tcp_link, store client ip + port
            if line_json.get("role") == "1":
                ip = line_json.get("client_ip")
            else:
                ip = line_json.get("server_ip")
            node_full.add(hostname + '.' + process_name + ',' + ip + ',' + server_port)
        else:
            # if ipvs_link, store vip + port and lip + port
            node_full.add(hostname + '.' + process_name + ',' +
			  line_json.get("virtual_ip") + ',' + line_json.get("virtual_port"))
            node_full.add(hostname + '.' + process_name + ',' + line_json.get("local_ip") + ',' + server_port)
        lines = f.readline()
    #print(node_full)

    # Add label to list
    # nodes_info_list's element include: key_id id label ip port
    label_list = []
    nodes_info_list = []
    for i in range(len(node_full)):
        node_list = node_full.pop()
        node_info = node_list.split(',')
        # write label to label_list without reprtition
        label_name = node_info[0]
        if not label_name in label_list:
            label_list.append(node_info[0])
        # write to nodes_info_list
        nodes_info_list.append((i, label_list.index(label_name), node_info[0], node_info[1], node_info[2]))
    #print(nodes_info_list)

    return nodes_info_list

if __name__ == '__main__':
    main()

