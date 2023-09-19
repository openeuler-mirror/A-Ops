import connexion
import six
import os
import requests
from flask import json
from io import StringIO

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.conf_host import ConfHost  # noqa: E501
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.excepted_conf_info import ExceptedConfInfo  # noqa: E501
from ragdoll.models.expected_conf import ExpectedConf  # noqa: E501
from ragdoll.models.real_conf_info import RealConfInfo  # noqa: E501
from ragdoll.models.sync_req import SyncReq
from ragdoll.models.sync_status import SyncStatus  # noqa: E501
from ragdoll.models.conf_base_info import ConfBaseInfo
from ragdoll.models.conf_is_synced import ConfIsSynced
from ragdoll.models.conf_synced_res import ConfSyncedRes
from ragdoll.models.realconf_base_info import RealconfBaseInfo
from ragdoll.models.host_sync_result import HostSyncResult
from ragdoll.models.host_sync_status import HostSyncStatus

from ragdoll.models.real_conf import RealConf
from ragdoll.controllers.format import Format
from ragdoll.utils.git_tools import GitTools
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.conf_tools import ConfTools
from ragdoll.utils.host_tools import HostTools
from ragdoll.utils.object_parse import ObjectParse
from ragdoll import util
from ragdoll.const.conf_files import yang_conf_list

TARGETDIR = GitTools().target_dir


def get_the_sync_status_of_domain(body=None):  # noqa: E501
    """
    get the status of the domain
    get the status of whether the domain has been synchronized # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: SyncStatus
    """

    if connexion.request.is_json:
        body = DomainName.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name

    check_res = Format.domainCheck(domain)
    if not check_res:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    # check the domian is exist
    is_exist = Format.isDomainExist(domain)
    if not is_exist:
        code_num = 404
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    # get the exist result of the host in domain
    is_host_list_exist = Format.isHostInDomain(domain)
    if not is_host_list_exist:
        code_num = 404
        base_rsp = BaseResponse(code_num, "The host information is not set in the current domain." +
                                "Please add the host information first")
        return base_rsp, code_num

    # get the host info in domain
    print("############## get the host in domain ##############")
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    url = "http://0.0.0.0:" + port + "/host/getHost"
    headers = {"Content-Type": "application/json"}
    host_body = DomainName(domain_name=domain)
    response = requests.post(url, data=json.dumps(host_body), headers=headers)  # post request
    res_code = response.status_code
    res_text = json.loads(response.text)
    print("return code is : {}".format(res_code))
    print("return text is : {}".format(res_text))

    if res_code != 200:
        code_num = res_code
        base_rsp = BaseResponse(code_num, "Failed to get host info in the current domain. " +
                                "The failure reason is:" + res_text.get('msg'))
        return base_rsp, code_num

    if len(res_text) == 0:
        code_num = 404

        base_rsp = BaseResponse(code_num, "The host currently controlled in the domain is empty." +
                                "Please add host information to the domain.")
        return base_rsp, code_num

    # get the host list from the git house
    host_tools = HostTools()
    host_ids = host_tools.getHostList(res_text)
    print("host_ids is : {}".format(host_ids))

    # get the managent conf in domain
    print("############## get the managent conf in domain ##############")
    get_man_conf_url = "http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    get_man_conf_body = DomainName(domain_name=domain)
    get_man_conf_res = requests.post(get_man_conf_url, data=json.dumps(get_man_conf_body),
                                     headers=headers)  # post request
    man_ronf_res_text = json.loads(get_man_conf_res.text)
    manage_confs = man_ronf_res_text.get("confFiles")
    print("manage_confs is : {}".format(manage_confs))

    if len(manage_confs) == 0:
        code_num = 404
        base_rsp = BaseResponse(code_num, "The configuration is not set in the current domain." +
                                "Please add the configuration information first.")
        return base_rsp, code_num

    # query the real conf in host
    print("############## query the real conf ##############")
    get_real_conf_url = "http://0.0.0.0:" + port + "/confs/queryRealConfs"
    query_real_body = ConfHost(domain_name=domain, host_ids=host_ids)
    get_res_conf_res = requests.post(get_real_conf_url, data=json.dumps(query_real_body),
                                     headers=headers)  # post request
    real_conf_res_code = get_res_conf_res.status_code
    real_conf_res_text = json.loads(get_res_conf_res.text)
    print("real_conf_res_text is : {}".format(real_conf_res_text))
    if real_conf_res_code != 200:
        code_num = real_conf_res_code
        base_rsp = BaseResponse(code_num, "Failed to get the real config of the all hosts in domain.")
        return base_rsp, code_num
    # Match the actual configuration with the expected configuration, and output the
    # configuration in the same format that can be compared with the expected result.
    sync_status = SyncStatus(domain_name=domain,
                             host_status=[])

    for d_real_conf in real_conf_res_text:
        host_id = d_real_conf.get("hostID")
        host_sync_status = HostSyncStatus(host_id=host_id,
                                          sync_status=[])
        d_real_conf_base = d_real_conf.get("confBaseInfos")
        for d_conf in d_real_conf_base:
            d_conf_path = d_conf.get("filePath")

            object_parse = ObjectParse()
            conf_type = object_parse.get_conf_type_by_conf_path(d_conf_path)
            conf_model = object_parse.create_conf_model_by_type(conf_type)

            comp_res = ""
            for d_man_conf in manage_confs:
                if d_man_conf.get("filePath").split(":")[-1] != d_conf_path:
                    continue
                # comp_res = conf_tools.compareManAndReal(d_conf.get("confContents"), d_man_conf.get("contents"))
                comp_res = conf_model.conf_compare(d_man_conf.get("contents"), d_conf.get("confContents"))
            conf_is_synced = ConfIsSynced(file_path=d_conf_path,
                                          is_synced=comp_res)
            host_sync_status.sync_status.append(conf_is_synced)

        sync_status.host_status.append(host_sync_status)

    # deal with not found files
    man_conf_list = []
    for d_man_conf in manage_confs:
        man_conf_list.append(d_man_conf.get("filePath").split(":")[-1])
    for d_host in sync_status.host_status:
        d_sync_status = d_host.sync_status
        file_list = []
        for d_file in d_sync_status:
            file_path = d_file.file_path
            file_list.append(file_path)
        for d_man_conf in man_conf_list:
            if d_man_conf in file_list:
                continue
            else:
                comp_res = "NOT FOUND"
                conf_is_synced = ConfIsSynced(file_path=d_man_conf,
                                              is_synced=comp_res)
                d_sync_status.append(conf_is_synced)

    return sync_status


def query_excepted_confs():  # noqa: E501
    """
    query the supported configurations in the current project
    queryExpectedConfs # noqa: E501

    :rtype: List[ExceptedConfInfo]
    """
    # get all domain
    print("############## get all domain ##############")
    cmd = "ls {}".format(TARGETDIR)
    git_tools = GitTools()
    res_domain = git_tools.run_shell_return_output(cmd).decode().split()

    if len(res_domain) == 0:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    success_domain = []
    all_domain_expected_files = []
    yang_modules = YangModule()
    for d_domian in res_domain:
        domain_path = os.path.join(TARGETDIR, d_domian)
        expected_conf_lists = ExceptedConfInfo(domain_name=d_domian,
                                               conf_base_infos=[])
        # Traverse all files in the source management repository
        for root, dirs, files in os.walk(domain_path):
            # Domain also contains host cache files, so we need to add hierarchical judgment for root
            if len(files) > 0 and len(root.split('/')) > 3:
                if "hostRecord.txt" in files:
                    continue
                for d_file in files:
                    feature = os.path.join(root.split('/')[-1], d_file)
                    d_module = yang_modules.getModuleByFeature(feature)
                    file_lists = yang_modules.getFilePathInModdule(yang_modules.module_list)
                    file_path = file_lists.get(d_module.name()).split(":")[-1]
                    d_file_path = os.path.join(root, d_file)
                    expected_value = Format.get_file_content_by_read(d_file_path)

                    git_tools = GitTools()
                    git_message = git_tools.getLogMessageByPath(d_file_path)

                    conf_base_info = ConfBaseInfo(file_path=file_path,
                                                  expected_contents=expected_value,
                                                  change_log=git_message)
                    expected_conf_lists.conf_base_infos.append(conf_base_info)
        all_domain_expected_files.append(expected_conf_lists)

    print("########################## expetedConfInfo ####################")
    print("all_domain_expected_files is : {}".format(all_domain_expected_files))
    print("########################## expetedConfInfo  end ####################")

    if len(all_domain_expected_files) == 0:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    return all_domain_expected_files


def query_real_confs(body=None):  # noqa: E501
    """
    query the real configuration value in the current hostId node

    query the real configuration value in the current hostId node # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: List[RealConfInfo]
    """
    if connexion.request.is_json:
        body = ConfHost.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    host_list = body.host_ids

    check_res = Format.domainCheck(domain)
    if not check_res:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    # check the domain is Exist
    is_exist = Format.isDomainExist(domain)
    if not is_exist:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    # check whether the host is configured in the domain
    is_host_list_exist = Format.isHostInDomain(domain)
    print("is_host_list_exist is : {}".format(is_host_list_exist))
    if not is_host_list_exist:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The host information is not set in the current domain." +
                                "Please add the host information first")
        return base_rsp, code_num

    # get all hosts managed by the current domain.
    # If host_list is empty, query all hosts in the current domain.
    # If host_list is not empty, the actual contents of the currently given host are queried.
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    exist_host = []
    failed_host = []
    if len(host_list) > 0:
        host_tool = HostTools()
        exist_host, failed_host = host_tool.getHostExistStatus(domain, host_list)
    else:
        print("############## get the host in domain ##############")
        url = "http://0.0.0.0:" + port + "/host/getHost"
        headers = {"Content-Type": "application/json"}
        get_man_host = DomainName(domain_name=domain)
        response = requests.post(url, data=json.dumps(get_man_host), headers=headers)  # post request
        print("host/getHost response is : {}".format(response.text))
        res_code = response.status_code
        res_text = json.loads(response.text)
        print("host/getHost return code is : {}".format(response.status_code))

    if len(exist_host) == 0 or len(failed_host) == len(host_list):
        code_num = 400
        base_rsp = BaseResponse(code_num, "The host information is not set in the current domain." +
                                "Please add the host information first")
        return base_rsp, code_num

    # get the management conf in domain
    print("############## get the management conf in domain ##############")
    url = "http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    get_man_conf_body = DomainName(domain_name=domain)
    print("body is : {}".format(get_man_conf_body))
    response = requests.post(url, data=json.dumps(get_man_conf_body), headers=headers)  # post request
    print("response is : {}".format(response.text))
    res_code = response.status_code
    res_text = json.loads(response.text)
    print("return code is : {}".format(response.status_code))

    if res_code != 200:
        code_num = res_code
        base_rsp = BaseResponse(code_num, "Failed to query the configuration items managed in the current domain. " +
                                "The failure reason is:" + res_text)
        return base_rsp, code_num
    conf_files = res_text.get("confFiles")
    if len(conf_files) == 0:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The configuration is not set in the current domain." +
                                "Please add the configuration information first")
        return base_rsp, code_num

    res = []

    # get the real conf in host
    conf_list = []
    for d_conf in conf_files:
        file_path = d_conf.get("filePath").split(":")[-1]
        conf_list.append(file_path)
    print("############## get the real conf in host ##############")
    get_real_conf_body = {}
    get_real_conf_body_info = []
    for d_host in exist_host:
        get_real_conf_body_infos = {}
        get_real_conf_body_infos["host_id"] = d_host
        get_real_conf_body_infos["config_list"] = conf_list
        get_real_conf_body_info.append(get_real_conf_body_infos)
    get_real_conf_body["infos"] = get_real_conf_body_info
    url = conf_tools.load_url_by_conf().get("collect_url")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(get_real_conf_body), headers=headers)  # post request
    resp = json.loads(response.text).get("data")
    resp_code = json.loads(response.text).get("code")
    if (resp_code != "200") and (resp_code != "206"):
        code_num = 404
        code_string = "Failed to obtain the actual configuration, please check the file exists."
        base_rsp = BaseResponse(code_num, code_string)
        return base_rsp, code_num

    if not resp or len(resp) == 0:
        code_num = 500
        code_string = "Failed to obtain the actual configuration, please check the host info for conf/collect."
        base_rsp = BaseResponse(code_num, code_string)
        return base_rsp, code_num
    success_lists = {}
    failed_lists = {}
    for d_res in resp:
        d_host_id = d_res.get("host_id")
        fail_files = d_res.get("fail_files")
        if len(fail_files) > 0:
            failed_lists["host_id"] = d_host_id
            failed_lists_conf = []
            for d_failed in fail_files:
                failed_lists_conf.append(d_failed)
            failed_lists["failed_conf"] = failed_lists_conf
            failed_lists["success_conf"] = []
        else:
            success_lists["host_id"] = d_host_id
            success_lists["success_conf"] = []
            success_lists["failed_conf"] = []

        read_conf_info = RealConfInfo(domain_name=domain,
                                      host_id=d_host_id,
                                      conf_base_infos=[])
        d_res_infos = d_res.get("infos")
        for d_file in d_res_infos:
            file_path = d_file.get("path")
            content = d_file.get("content")
            object_parse = ObjectParse()
            content_string = object_parse.parse_conf_to_json(file_path, content)
            file_atrr = d_file.get("file_attr").get("mode")
            file_owner = "({}, {})".format(d_file.get("file_attr").get("group"), d_file.get("file_attr").get("owner"))
            real_conf_base_info = RealconfBaseInfo(file_path=file_path,
                                                   file_attr=file_atrr,
                                                   file_owner=file_owner,
                                                   conf_contens=content_string)
            read_conf_info.conf_base_infos.append(real_conf_base_info)
            if len(fail_files) > 0:
                failed_lists.get("success_conf").append(file_path)
            else:
                success_lists.get("success_conf").append(file_path)
        res.append(read_conf_info)

    print("***************************************")
    print("success_lists is : {}".format(success_lists))
    print("failed_lists is : {}".format(failed_lists))

    if len(res) == 0:
        code_num = 400
        res_text = "The real configuration does not found."
        base_rsp = BaseResponse(code_num, "Real configuration query failed." +
                                "The failure reason is : " + res_text)
        return base_rsp, code_num

    return res


def sync_conf_to_host_from_domain(body=None):  # noqa: E501
    """
    synchronize the configuration information of the configuration domain to the host # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: List[HostSyncResult]
    """
    if connexion.request.is_json:
        body = SyncReq.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    sync_list = body.sync_list

    host_sync_confs = dict()

    for sync in sync_list:
        host_sync_confs[sync.host_id] = sync.sync_configs

    # check the input domain
    check_res = Format.domainCheck(domain)
    if not check_res:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    #  check whether the domain exists
    is_exist = Format.isDomainExist(domain)
    if not is_exist:
        code_num = 404
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    # get the management host in domain
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    print("############## get host in domain ##############")
    url = "http://0.0.0.0:" + port + "/host/getHost"
    headers = {"Content-Type": "application/json"}
    get_host_body = DomainName(domain_name=domain)
    response = requests.post(url, data=json.dumps(get_host_body), headers=headers)  # post request
    res_host_code = response.status_code
    res_host_text = json.loads(response.text)

    # Check whether the host is in the managed host list
    exist_host = []
    if len(host_sync_confs) > 0:
        host_ids = host_sync_confs.keys()
        for host_id in host_ids:
            for d_host in res_host_text:
                if host_id == d_host.get("hostId"):
                    exist_host.append(host_id)
    else:
        for d_host in res_host_text:
            temp_host = {}
            temp_host["hostId"] = d_host.get("hostId")
            exist_host.append(temp_host)
    print("exist_host is : {}".format(exist_host))

    if len(exist_host) == 0:
        code_num = 400
        base_rsp = BaseResponse(code_num, "The host information is not set in the current domain." +
                                "Please add the host information first")
        return base_rsp, code_num

    # get the management conf in domain
    print("############## get management conf in domain ##############")
    get_man_conf_url = "http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    get_man_conf_body = DomainName(domain_name=domain)
    get_man_conf_res = requests.post(get_man_conf_url, data=json.dumps(get_man_conf_body),
                                     headers=headers)  # post request
    man_conf_res_text = json.loads(get_man_conf_res.text)
    manage_confs = man_conf_res_text.get("confFiles")
    print("manage_confs is : {}".format(manage_confs))

    # Deserialize and reverse parse the expected configuration
    sync_res = []
    for host_id in exist_host:
        host_sync_result = HostSyncResult(host_id=host_id,
                                          sync_result=[])
        sync_confs = host_sync_confs.get(host_id)
        for d_man_conf in manage_confs:
            file_path = d_man_conf.get("filePath").split(":")[-1]
            if file_path in sync_confs:
                file_path = d_man_conf.get("filePath").split(":")[-1]
                contents = d_man_conf.get("contents")
                object_parse = ObjectParse()
                content = object_parse.parse_json_to_conf(file_path, contents)
                # Configuration to the host
                sync_conf_url = conf_tools.load_url_by_conf().get("sync_url")
                headers = {"Content-Type": "application/json"}
                data = {"host_id": host_id, "file_path": file_path, "content": content}
                sync_response = requests.put(sync_conf_url, data=json.dumps(data), headers=headers)

                resp_code = json.loads(sync_response.text).get('code')
                resp = json.loads(sync_response.text).get('data').get('resp')
                conf_sync_res = ConfSyncedRes(file_path=file_path,
                                              result="")
                if resp_code == "200" and resp.get('sync_result') is True:
                    conf_sync_res.result = "SUCCESS"
                else:
                    conf_sync_res.result = "FAILED"
                host_sync_result.sync_result.append(conf_sync_res)
        sync_res.append(host_sync_result)

    return sync_res


def query_supported_confs(body=None):
    """
        query supported configuration list # noqa: E501

       :param body:
       :type body: dict | bytes

       :rtype: List
    """
    if connexion.request.is_json:
        body = DomainName.from_dict(connexion.request.get_json())

    domain = body.domain_name

    check_res = Format.domainCheck(domain)
    if not check_res:
        code_num = 400
        base_rsp = BaseResponse(code_num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, code_num

    is_exist = Format.isDomainExist(domain)
    if not is_exist:
        code_num = 404
        base_rsp = BaseResponse(code_num, "The current domain does not exist, please create the domain first.")
        return base_rsp, code_num

    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    url = "http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    get_man_conf_body = DomainName(domain_name=domain)
    print("body is : {}".format(get_man_conf_body))
    response = requests.post(url, data=json.dumps(get_man_conf_body), headers=headers)  # post request
    print("response is : {}".format(response.text))
    res_code = response.status_code
    res_json = json.loads(response.text)
    print("return code is : {}".format(response.status_code))

    if res_code != 200:
        code_num = res_code
        base_rsp = BaseResponse(code_num,
                                "Failed to query the configuration items managed in the current domain. " +
                                "The failure reason is:" + res_json)
        return base_rsp, code_num

    conf_files = res_json.get("confFiles")
    if len(conf_files) == 0:
        return yang_conf_list

    exist_conf_list = []
    for conf in conf_files:
        exist_conf_list.append(conf.get('filePath'))

    return list(set(yang_conf_list).difference(set(exist_conf_list)))
