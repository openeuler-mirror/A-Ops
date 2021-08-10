import os

def get_temp_file_path():
    pos = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    #print(pos)
    temp_tcp_files = []
    temp_other_files = []
    conf_files = []
    for root, dirs, files in os.walk(pos, topdown=True):
        for name in files:
            txt_path = os.path.join(root, name)
            if os.path.splitext(name)[0] in ["tcpline"]:
                temp_tcp_files.append(txt_path)
            if os.path.splitext(name)[0] in ["otherline"]:
                temp_other_files.append(txt_path)
            if os.path.splitext(name)[1] in [".conf"]:
                conf_files.append(txt_path)

    #print("ac tcp:", temp_tcp_files)
    #print("ac other:", temp_other_files)
    return temp_tcp_files, temp_other_files, conf_files

#get_temp_file_path()