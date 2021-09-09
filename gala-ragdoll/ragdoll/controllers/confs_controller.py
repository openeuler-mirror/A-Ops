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
from ragdoll.models.sync_status import SyncStatus  # noqa: E501
from ragdoll.models.conf_base_info import ConfBaseInfo
from ragdoll.models.conf_is_synced import ConfIsSynced
from ragdoll.models.conf_synced_res import ConfSyncedRes
from ragdoll.models.realconf_base_info import RealconfBaseInfo
from ragdoll.models.host_sync_result import HostSyncResult
from ragdoll.models.host_sync_status import HostSyncStatus
from ragdoll.parses.ini_parse import IniJsonParse
from ragdoll.models.real_conf import RealConf
from ragdoll.controllers.format import Format
from ragdoll.utils.git_tools import GitTools
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.conf_tools import ConfTools
from ragdoll.utils.host_tools import HostTools
from ragdoll.utils.object_parse import ObjectParse
from ragdoll import util

TARGETDIR = GitTools().target_dir

def get_the_sync_status_of_domain(body=None):  # noqa: E501
    """get the status of the domain

    get the status of whether the domain has been synchronized # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: SyncStatus
    """

    if connexion.request.is_json:
        body = DomainName.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name

    # check the domian is exist
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # get the exist result of the host in domain
    isHostListExist = Format.isHostInDomain(domain)
    if not isHostListExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # get the host info in domain
    print("############## get the host in domain ##############")
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    url="http://0.0.0.0:" + port + "/host/getHost"
    headers = {"Content-Type": "application/json"}
    getHostBody = DomainName(domain_name = domain)
    response = requests.post(url, data=json.dumps(getHostBody), headers=headers)  # post request
    resCode = response.status_code
    resText = json.loads(response.text)
    print("return code is : {}".format(resCode))
    print("return text is : {}".format(resText))

    if resCode != 200:
        codeNum = resCode
        base_rsp = BaseResponse(codeNum, "Failed to get host info in the current domain. " + 
                                         "The failure reason is:" + resText)
        return base_rsp, codeNum

    if len(resText) == 0:
        codeNum = 404

        base_rsp = BaseResponse(codeNum, "The host currently controlled in the domain is empty." + 
                                         "Please add host information to the domain.")
        return base_rsp, codeNum

    # get the host list from the git house
    hostTools = HostTools()
    hostIds = hostTools.getHostList(resText)
    print("hostIds is : {}".format(hostIds))

    # get the managent conf in domain
    print("############## get the managent conf in domain ##############")
    getManConfUrl="http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    getManConfRes = requests.post(getManConfUrl, data=json.dumps(getManConfBody), headers=headers)  # post request
    manConfResText = json.loads(getManConfRes.text)
    manageConfs = manConfResText.get("confFiles")
    print("manageConfs is : {}".format(manageConfs))

    if len(manageConfs) == 0:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The configuration is not set in the current domain." + 
                                        "Please add the configuration information first.")
        return base_rsp, codeNum

    # query the real conf in host
    print("############## query the real conf ##############")
    getRealConfUrl = "http://0.0.0.0:" + port + "/confs/queryRealConfs"
    queryRealBody = ConfHost(domain_name = domain, host_ids = hostIds)
    getResConfRes = requests.post(getRealConfUrl, data=json.dumps(queryRealBody), headers=headers)  # post request
    realConfResCode = getResConfRes.status_code
    realConfResText = json.loads(getResConfRes.text)
    print("realConfResText is : {}".format(realConfResText))
    if realConfResCode != 200:
        codeNum = realConfResCode
        base_rsp = BaseResponse(codeNum, "Failed to get the real config of the all hosts in domain.")
        return base_rsp, codeNum
    # Match the actual configuration with the expected configuration, and output the 
    # configuration in the same format that can be compared with the expected result.
    sync_status = SyncStatus(domain_name = domain,
                             host_status = [])

    for d_real_conf in realConfResText:
        host_id = d_real_conf.get("hostID")
        host_sync_status = HostSyncStatus(host_id = host_id,
                                          sync_status = [])
        d_real_conf_base = d_real_conf.get("confBaseInfos")
        for d_conf in d_real_conf_base:
            d_conf_path = d_conf.get("filePath")
            comp_res = ""
            for d_man_conf in manageConfs:
                if d_man_conf.get("filePath").split(":")[-1] == d_conf_path:
                    comp_res = conf_tools.compareManAndReal(d_conf.get("confContents"), d_man_conf.get("contents"))
                    break
            conf_is_synced = ConfIsSynced(file_path = d_conf_path,
                                          is_synced = comp_res)
            host_sync_status.sync_status.append(conf_is_synced)

        sync_status.host_status.append(host_sync_status)

    # deal with not found files
    man_conf_list = []
    for d_man_conf in manageConfs:
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
                conf_is_synced = ConfIsSynced(file_path = d_man_conf,
                                              is_synced = comp_res)
                d_sync_status.append(conf_is_synced)

    return sync_status


def query_excepted_confs():  # noqa: E501
    """query the supported configurations in the current project

    queryExpectedConfs # noqa: E501

    :rtype: List[ExceptedConfInfo]
    """
    # get all domain
    print("############## get all domain ##############")
    cmd = "ls {}".format(TARGETDIR)
    gitTools = GitTools()
    res_domain = gitTools.run_shell_return_output(cmd).decode().split()

    if len(res_domain) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    success_domain = []
    all_domain_expected_files = []
    yang_modules = YangModule()
    for d_domian in res_domain:
        domain_path = os.path.join(TARGETDIR, d_domian)
        expected_conf_lists = ExceptedConfInfo(domain_name = d_domian,
                                               conf_base_infos = [])
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
                    expectedValue = Format.get_file_content_by_read(d_file_path)

                    git_tools = GitTools()
                    gitMessage = git_tools.getLogMessageByPath(d_file_path)

                    conf_base_info = ConfBaseInfo(file_path = file_path,
                                                  expected_contents = expectedValue,
                                                  change_log = gitMessage)
                    expected_conf_lists.conf_base_infos.append(conf_base_info)
        all_domain_expected_files.append(expected_conf_lists)

    print("########################## expetedConfInfo ####################")
    print("all_domain_expected_files is : {}".format(all_domain_expected_files))
    print("########################## expetedConfInfo  end ####################")

    if len(all_domain_expected_files) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    return all_domain_expected_files


def query_real_confs(body=None):  # noqa: E501
    """query the real configuration value in the current hostId node

    query the real configuration value in the current hostId node # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: List[RealConfInfo]
    """
    if connexion.request.is_json:
        body = ConfHost.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    hostList = body.host_ids
    # check the domain is Exist
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum
    # check whether the host is configured in the domain
    isHostListExist = Format.isHostInDomain(domain)
    print("isHostListExist is : {}".format(isHostListExist))
    if not isHostListExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # get all hosts managed by the current domain. 
    # If hostList is empty, query all hosts in the current domain.
    # If hostList is not empty, the actual contents of the currently given host are queried.
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    if len(hostList) > 0:
        hostTool = HostTools()
        existHost, failedHost = hostTool.getHostExistStatus(domain, hostList)
    else:
        print("############## get the host in domain ##############")
        url="http://0.0.0.0:" + port + "/host/getHost"
        headers = {"Content-Type": "application/json"}
        get_man_host = DomainName(domain_name=domain)
        response = requests.post(url, data=json.dumps(get_man_host), headers=headers)  # post request
        print("host/getHost response is : {}".format(response.text))
        resCode = response.status_code
        resText = json.loads(response.text)
        print("host/getHost return code is : {}".format(response.status_code))


    if len(existHost) == 0 or len(failedHost) == len(hostList):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # get the management conf in domain
    print("############## get the management conf in domain ##############")
    url="http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    print("body is : {}".format(getManConfBody))
    response = requests.post(url, data=json.dumps(getManConfBody), headers=headers)  # post request
    print("response is : {}".format(response.text))
    resCode = response.status_code
    resText = json.loads(response.text)
    print("return code is : {}".format(response.status_code))

    if resCode != 200:
        codeNum = resCode
        base_rsp = BaseResponse(codeNum, "Failed to query the configuration items managed in the current domain. " + 
                                         "The failure reason is:" + resText)
        return base_rsp, codeNum
    conf_files = resText.get("confFiles")
    if len(conf_files) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The configuration is not set in the current domain." + 
                                        "Please add the configuration information first")
        return base_rsp, codeNum

    res = []

    # get the real conf in host
    conf_list = []
    for d_conf in conf_files:
        file_path = d_conf.get("filePath").split(":")[-1]
        conf_list.append(file_path)
    print("############## get the real conf in host ##############")
    get_real_conf_body = {}
    get_real_conf_body_info = []
    for d_host in existHost:
        get_real_conf_body_infos = {}
        get_real_conf_body_infos["host_id"] = d_host
        get_real_conf_body_infos["config_list"] = conf_list
        get_real_conf_body_info.append(get_real_conf_body_infos)
    get_real_conf_body["infos"] = get_real_conf_body_info
    url = conf_tools.load_collect_by_conf()
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(get_real_conf_body), headers=headers)  # post request
    reps = json.loads(response.text).get("resp")
    resp_code = json.loads(response.text).get("code")
    if (resp_code != 200) and (resp_code != 206):
        codeNum = 404
        codeString = "Failed to obtain the actual configuration, please check the file exists."
        base_rsp = BaseResponse(codeNum, codeString)
        return base_rsp, codeNum

    if not reps or len(reps) == 0:
        codeNum = 500
        codeString = "Failed to obtain the actual configuration, please check the host info for conf/collect."
        base_rsp = BaseResponse(codeNum, codeString)
        return base_rsp, codeNum
    success_lists = {}
    failed_lists = {}
    for d_res in reps:
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

        read_conf_info = RealConfInfo(domain_name = domain,
                                      host_id = d_host_id,
                                      conf_base_infos = [])
        d_res_infos = d_res.get("infos")
        for d_file in d_res_infos:
            file_path = d_file.get("path")
            content = d_file.get("content")
            object_parse = ObjectParse()
            content_string = object_parse.parse_content_to_json(file_path, content)
            file_atrr = d_file.get("file_attr").get("mode")
            file_owner = "(" + d_file.get("file_attr").get("group") + ", " + d_file.get("file_attr").get("owner") + ")"
            real_conf_base_info = RealconfBaseInfo(file_path = file_path,
                                                   file_attr = file_atrr,
                                                   file_owner = file_owner,
                                                   conf_contens = content_string)
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
        codeNum = 400
        resText = "The real configuration does not found."
        base_rsp = BaseResponse(codeNum, "Real configuration query failed." +
                                        "The failure reason is : " + resText)
        return base_rsp, codeNum

    return res


def sync_conf_to_host_from_domain(body=None):  # noqa: E501
    """
    synchronize the configuration information of the configuration domain to the host # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: List[HostSyncResult]
    """
    if connexion.request.is_json:
        body = ConfHost.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    hostList = body.host_ids

    #  check whether the domain exists
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # get the management host in domain
    conf_tools = ConfTools()
    port = conf_tools.load_port_by_conf()
    print("############## get host in domain ##############")
    url="http://0.0.0.0:" + port + "/host/getHost"
    headers = {"Content-Type": "application/json"}
    getHostBody = DomainName(domain_name = domain)
    response = requests.post(url, data=json.dumps(getHostBody), headers=headers)  # post request
    resHostCode = response.status_code
    resHostText = json.loads(response.text)

    # Check whether the host is in the managed host list
    existHost = []
    if len(hostList) > 0:
        for host in hostList:
            for d_host in resHostText:
                if host.get("hostId") == d_host.get("hostId"):
                    existHost.append(host)
    else:
        for d_host in resHostText:
            temp_host = {}
            temp_host["hostId"] = d_host.get("hostId")
            existHost.append(temp_host)
    print("existHost is : {}".format(existHost))

    if len(existHost) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # get the management conf in domain
    print("############## get management conf in domain ##############")
    getManConfUrl="http://0.0.0.0:" + port + "/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    getManConfRes = requests.post(getManConfUrl, data=json.dumps(getManConfBody), headers=headers)  # post request
    manConfResText = json.loads(getManConfRes.text)
    manageConfs = manConfResText.get("confFiles")
    print("manageConfs is : {}".format(manageConfs))

    # Deserialize and reverse parse the expected configuration
    sync_res = []
    for d_host in existHost:
        host_sync_result = HostSyncResult(host_id = d_host,
                           sync_result = [])
        for d_man_conf in manageConfs:
            file_path = d_man_conf.get("filePath").split(":")[-1]
            contents = d_man_conf.get("contents")
            object_parse = ObjectParse()
            content = object_parse.parse_json_to_content(file_path, contents)
            # Configuration to the host
            result = conf_tools.wirteFileInPath(file_path, content)
            conf_sync_res = ConfSyncedRes(file_path = file_path,
                                          result = "")
            if result:
                conf_sync_res.result = "SUCCESS"
            else:
                conf_sync_res.result = "FILED"
            host_sync_result.sync_result.append(conf_sync_res)
        sync_res.append(host_sync_result)

    return sync_res
