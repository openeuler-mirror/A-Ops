import os

def entity_name(hostname, process_name, table_name):
    if table_name == None:
        return hostname + '.' + process_name
    else:
        return process_name + '.' + table_name