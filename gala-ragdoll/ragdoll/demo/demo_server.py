import connexion

from ragdoll.models.conf_host import ConfHost

def _read_file(path):
    info = ""
    try:
        with open(path, "r") as f:
            info = f.read()
    except IOError as error:
        print(error)
    return info

def collect_conf(body=None):
    """
    get configuration information from the specified path.
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
    
    resp = []
    rsp = {"code": 400, "msg": "Failed to verify the input parameter, please check the input parameters.", "resp": resp}
    request_infos = body.get("infos")
    if len(request_infos) == 0:
        return rsp
    
    success_flag = False
    failure_flag = False
    for req in request_infos:
        conf_list = req["config_list"]
        if len(conf_list) == 0:
            return rsp

        _resp = {"host_id": req["host_id"], "infos":[], "fail_files":[]}
        for conf_path in conf_list:
            conf_info = _read_file(conf_path)
            if conf_info:
                _infos = {"path": conf_path,
                          "content": conf_info,
                          "file_attr": {"mode":"777", "group":"root", "owner":"root"},
                          "file_owner": "yy"}
                _resp["infos"].append(_infos)
                success_flag = True
            else:
                _resp["fail_files"].append(conf_path)
                failure_flag = True
        resp.append(_resp)
    
    if not failure_flag:
        rsp["code"] = 200
        rsp["msg"] = "The configuration file is collected successfully."

    if not success_flag:
        rsp["code"] = 500
        rsp["msg"] = "Failed to collect configuration data"

    rsp["code"] = 206
    rsp["msg"] = "Some configurations fail to be collected."
    return rsp

def _write_file(path, content):
    status = False
    error_info = ""
    try:
        with open(path, "w+") as f:
            f.writelines(content)
            status = True
    except IOError as error:
        error_info = error
        print(error)
    return status, error_info

def sync_conf(body=None):
    if connexion.request.is_json:
        body = connexion.request.get_json()
    host_id = body.get("host_id")
    conf_path = body.get("file_path")
    content = body.get("content")
    
    rsp = {"code": 200, "msg": "Configuration synchronization succeeded.", "status": True}
    if not host_id or not conf_path or not content:
        rsp = {"code": 400, 
               "msg": "Failed to verify the input parameter, please check the input parameters.", 
               "status": False}
        return rsp
    
    status, error_info = _write_file(conf_path, content)
    if not status:
        rsp = {"code": 500, 
               "msg": "Failed to synchronize the configuration. ERROR:{}".format(error_info), 
               "status": False}
    return rsp