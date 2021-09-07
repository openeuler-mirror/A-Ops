import os

# node entity id
def node_entity_name(dst_hostname, dst_proc_name, table_name):
    return dst_hostname + '.' + dst_proc_name

# line entity id
def edge_entity_name(table_name, dst_hostname, dst_proc_name, src_hostname, src_proc_name):
    if dst_hostname == None or src_hostname == None:
        return src_proc_name + '.' + dst_proc_name + '.' + table_name
    else:
        return src_hostname + '.' + src_proc_name + '.' + dst_hostname + '.' + dst_proc_name + '.' + table_name