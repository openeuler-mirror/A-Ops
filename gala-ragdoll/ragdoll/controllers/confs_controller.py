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
from ragdoll.parses.ini_parse import IniJsonParser
from ragdoll.models.real_conf import RealConf
from ragdoll.controllers.format import Format
from ragdoll.utils.git_tools import GitTools
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.conf_tools import ConfTools
from ragdoll.utils.host_tools import HostTools
from ragdoll.utils.object_parse import ObjectParse
from ragdoll import util

TARGETDIR = "/home/confTrace"

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

    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # 获取domain内管控的host信息
    isHostListExist = Format.isHostInDomain(domain)
    if not isHostListExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # 获取domain域内管控的所有host
    print("############## 获取domain内纳管的host信息 ##############")
    url="http://0.0.0.0:8080/host/getHost"
    headers = {"Content-Type": "application/json"}
    getHostBody = DomainName(domain_name = domain)
    response = requests.get(url, data=json.dumps(getHostBody), headers=headers)  # 发送请求
    resCode = response.status_code
    resText = json.loads(response.text)
    print("return code is : {}".format(resCode))
    print("return text is : {}".format(resText))

    if resCode is not 200:
        codeNum = resCode
        base_rsp = BaseResponse(codeNum, "Failed to get host info in the current domain. " + 
                                         "The failure reason is:" + resText)
        return base_rsp, codeNum

    if len(resText) == 0:
        codeNum = 404

        base_rsp = BaseResponse(codeNum, "The host currently controlled in the domain is empty." + 
                                         "Please add host information to the domain.")
        return base_rsp, codeNum

    # 从纳管host结果中提取host列表
    hostTools = HostTools()
    hostIds = hostTools.getHostList(resText)
    print("hostIds is : {}".format(hostIds))

    # 获取当前domain域的预期配置
    getManConfInDomainBody = DomainName(domain_name = "OS")
    print("############## 获取domain内纳管的配置项 ##############")
    getManConfUrl="http://0.0.0.0:8080/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    getManConfRes = requests.get(getManConfUrl, data=json.dumps(getManConfBody), headers=headers)  # 发送请求
    manConfResCode = getManConfRes.status_code
    manConfResText = json.loads(getManConfRes.text)
    print("manConfResText is : {}".format(manConfResText))
    manageConfs = manConfResText.get("confFiles")
    print("manageConfs is : {}".format(manageConfs))

    # 调用查询真实配置的接口，获取真实配置
    print("############## 获取真实配置 ##############")
    getRealConfUrl = "http://0.0.0.0:8080/confs/queryRealConfs"
    queryRealBody = ConfHost(domain_name = domain, host_ids = hostIds)
    # print("queryRealBody is : {}".format(queryRealBody))
    getResConfRes = requests.get(getRealConfUrl, data=json.dumps(queryRealBody), headers=headers)  # 发送请求
    realConfResCode = getResConfRes.status_code
    realConfResText = json.loads(getResConfRes.text)

    print("realConfResText is : {}".format(realConfResText))


    # 将实际配置与预期配置进行匹配，输出可以与预期结果进行对比的同等格式的配置
    conf_tools = ConfTools()
    sync_status = SyncStatus(domain_name = domain,
                             host_status = [])

    for d_real_conf in realConfResText:
        host_id = d_real_conf.get("hostID")
        host_sync_status = HostSyncStatus(host_id = host_id,
                                          sync_status = [])
        d_real_conf_base = d_real_conf.get("confBaseInfos")
        for d_conf in d_real_conf_base:
            print("\n")
            print("d_conf is : {}".format(d_conf))
            d_conf_path = d_conf.get("filePath")
            comp_res = ""
            for d_man_conf in manageConfs:
                if d_man_conf.get("filePath").split(":")[-1] == d_conf_path:
                    comp_res = conf_tools.compareManAndReal(d_conf.get("confContents"), d_man_conf.get("contents"))
                if comp_res is "":
                    comp_res = "NOT FOUND"
            conf_is_synced = ConfIsSynced(file_path = d_conf_path,
                                          is_synced = comp_res)
            host_sync_status.sync_status.append(conf_is_synced)

        sync_status.host_status.append(host_sync_status)

    return sync_status


def query_excepted_confs(range):  # noqa: E501
    """query the supported configurations in the current project

    queryExpectedConfs # noqa: E501

    :rtype: List[ExceptedConfInfo]
    """
    print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")

    # 获取当前所有的domain
    print("############## 获取所有的domain列表 ##############")
    cmd = "ls {}".format(TARGETDIR)
    gitTools = GitTools()
    res_domain = gitTools.run_shell_return_output(cmd).decode().split()

    if len(res_domain) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    success_domain = []
    failed_failed = []
    all_domain_expected_files = []
    for d_domian in res_domain:
        domain_path = os.path.join(TARGETDIR, d_domian)
        expected_conf_lists = ExceptedConfInfo(domain_name = d_domian,
                                               conf_base_infos = [])
        # 路径下存在文件时即判断为配置项的path
        for root, dirs, files in os.walk(domain_path):
            conf_base_infos = []
            # domain下还含有host缓存文件，所以需要增加对于root的层次判断
            if len(files) > 0 and len(root.split('/')) > 3:
                if "hostRecord.txt" in files:
                    continue
                confPath = root.split('/', 3)[3]
                for d_file in files:
                    d_file_path = os.path.join(root, d_file)

                    expectedValue = Format.get_file_content_by_read(d_file_path)

                    git_tools = GitTools()
                    gitMessage = git_tools.getLogMessageByPath(d_file_path)
                    feature = os.path.join(root.split('/')[-1], d_file)

                    yang_modules = YangModule()
                    d_module = yang_modules.getModuleByFeature(feature)
                    file_lists = yang_modules.getFilePathInModdule(yang_modules._module_list)
                    d_module_path = file_lists.get(d_module.name())

                    conf_base_info = ConfBaseInfo(file_path = os.path.join(confPath, d_file),
                                                module_path = d_module_path,
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
    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum
    # 先check domain内是否已经配置host
    isHostListExist = Format.isHostInDomain(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # 获取当前domain纳管的所有host. 如果hostList为空，咋查询当前domain内所有的host。
    # hostList不为空，则查询当前给定的host的实际内容。
    if len(hostList) > 0 :
        hostTool = HostTools()
        existHost, failedHost = hostTool.getHostExistStatus(domain, hostList)
    else:
        print("############## 获取domain内纳管的host ##############")
        url="http://0.0.0.0:8080/host/getHost"
        headers = {"Content-Type": "application/json"}
        get_man_host = DomainName(domain_name=domain)
        response = requests.get(url, data=json.dumps(get_man_host), headers=headers)  # 发送请求
        print("host/getHost response is : {}".format(response.text))
        resCode = response.status_code
        resText = json.loads(response.text)
        print("host/getHost return code is : {}".format(response.status_code))


    if len(existHost) == 0 or len(failedHost) == len(hostList):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." + 
                                          "Please add the host information first")
        return base_rsp, codeNum

    # 获取domain内纳管的配置项
    # getManConfInDomainBody = DomainName(domain_name = "OS")
    print("############## 获取domain内纳管的配置项 ##############")
    url="http://0.0.0.0:8080/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    response = requests.get(url, data=json.dumps(getManConfBody), headers=headers)  # 发送请求
    print("response is : {}".format(response.text))
    resCode = response.status_code
    resText = json.loads(response.text)
    print("return code is : {}".format(response.status_code))

    if resCode is not 200:
        codeNum = resCode
        base_rsp = BaseResponse(codeNum, "Failed to query the configuration items managed in the current domain. " + 
                                         "The failure reason is:" + resText)
        return base_rsp, codeNum
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    print("resText type is : {}".format(type(resText)))
    conf_files = resText.get("confFiles")
    if len(conf_files) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The configuration is not set in the current domain." + 
                                        "Please add the configuration information first")
        return base_rsp, codeNum

    res = []
    success_host = []
    failed_host = []
    print("existHost is : {}".format(existHost))
    for host in existHost:
        success_conf = []
        failed_conf = []
        read_conf_info = RealConfInfo(domain_name = domain,
                                      host_id = host,
                                      conf_base_infos = [])
        for d_conf in conf_files:
            file_path = d_conf.get("filePath").split(":")[-1]
            # 判断文件是否存在
            isExistes = Format.is_exists_file(file_path)
            if not isExistes:
                real_conf = RealconfBaseInfo(path = file_path)
                read_conf_info.conf_base_infos.append(real_conf)
                continue
            # file存在，则获取实际配置
            content = Format.get_file_content_by_read(file_path)
            # 配置解析和转换
            object_parse = ObjectParse()
            content_string = object_parse.parse_content_to_json(file_path, content)
            print("content_string is : {}".format(content_string))

            # file存在，获取配置所属rpm的信息
            conf_tools = ConfTools()
            pkg_name, pkg_release, pkg_version = conf_tools.getRpmInfo(file_path)
            print("the pkg info is : {name}  {version}  {release}".format(name=pkg_name, release=pkg_release, version=pkg_version))

            # file存在，获取配置的文件属性信息
            file_atrr, file_owner = conf_tools.getFileAttr(file_path)
            print("the file attr info is : {file_atrr}  {file_owner}".format(file_atrr=file_atrr, file_owner=file_owner))

            # 保存原版配置文件
            git_file = conf_tools.writeBakFileInPath(file_path, content)

            real_conf_base_info = RealconfBaseInfo(file_path = file_path,
                                                   rpm_name = pkg_name,
                                                   rpm_version = pkg_version,
                                                   rpm_release = pkg_release,
                                                   file_attr = file_atrr,
                                                   file_owner = file_owner,
                                                   conf_contens = content_string)
            read_conf_info.conf_base_infos.append(real_conf_base_info)
        res.append(read_conf_info)

    print("res is : {}".format(res))

    if len(res) == 0:
        codeNum = 400
        resText = "The real configuration does not found."
        base_rsp = BaseResponse(codeNum, "Real configuration query failed." +
                                        "The failure reason is : " + resText)
        return base_rsp, codeNum

    # 拼接返回值
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

    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 404
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # 获取domain域内管控的所有host
    print("############## 获取domain内纳管的host信息 ##############")
    url="http://0.0.0.0:8080/host/getHost"
    headers = {"Content-Type": "application/json"}
    getHostBody = DomainName(domain_name = domain)
    response = requests.get(url, data=json.dumps(getHostBody), headers=headers)  # 发送请求
    resHostCode = response.status_code
    resHostText = json.loads(response.text)
    print("return resHostCode is : {}".format(resHostCode))
    print("return resHostText is : {}".format(resHostText))

    # # check 入参的host是否在domain内
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

    # 查询预期配置
    print("############## 获取domain内纳管的配置项 ##############")
    getManConfUrl="http://0.0.0.0:8080/management/getManagementConf"
    headers = {"Content-Type": "application/json"}
    getManConfBody = DomainName(domain_name=domain)
    getManConfRes = requests.get(getManConfUrl, data=json.dumps(getManConfBody), headers=headers)  # 发送请求
    manConfResCode = getManConfRes.status_code
    manConfResText = json.loads(getManConfRes.text)
    manageConfs = manConfResText.get("confFiles")
    print("manageConfs is : {}".format(manageConfs))

    # 将预期配置进行反序列化和反解析
    sync_res = []
    conf_tools = ConfTools()
    for d_host in existHost:
        host_sync_result = HostSyncResult(host_id = d_host,
                           sync_result = [])
        for d_man_conf in manageConfs:
            file_path = d_man_conf.get("filePath").split(":")[-1]
            contents = d_man_conf.get("contents")
            object_parse = ObjectParse()
            content = object_parse.parse_json_to_object(file_path, contents)
            print("content is : {}".format(content))
            # 配置写入 host
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