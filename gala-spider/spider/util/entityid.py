import os

# node entity id
def node_entity_name(dst_hostname, dst_proc_name):
    return dst_hostname + '.' + dst_proc_name

# line entity id
def edge_entity_name(table_name, dst_hostname, dst_proc_name, src_hostname, src_proc_name):
    if dst_proc_name is None:
        print("edge_entity_name get entity id fail, because dst_proc_name is None, please check")
        return None
    if src_proc_name is None:
        print("edge_entity_name get entity id fail, because src_proc_name is None, please check")
        return None

    if dst_hostname is None or src_hostname is None:
        return src_proc_name + '.' + dst_proc_name + '.' + table_name
    else:
        return src_hostname + '.' + src_proc_name + '.' + dst_hostname + '.' + dst_proc_name + '.' + table_name
