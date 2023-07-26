import connexion
import six
import os
import json
import re
import ast

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.host import Host  # noqa: E501
from ragdoll.models.host_infos import HostInfos  # noqa: E501
from ragdoll import util
from ragdoll.controllers.format import Format
from ragdoll.utils.git_tools import GitTools

TARGETDIR = GitTools().target_dir

def add_host_in_domain(body=None):  # noqa: E501
    """add host in the configuration domain

    add host in the configuration domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: BaseResponse
    """
    if connexion.request.is_json:
        body = HostInfos.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    host_infos = body.host_infos

    # check whether host_infos is empty
    if len(host_infos) == 0:
        num = 400
        base_rsp = BaseResponse(num, "Enter host info cannot be empty, please check the host info.")
        return base_rsp, num

    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    # check whether the domain exists
    isExist = Format.isDomainExist(domain)
    if not isExist:
        num = 400
        base_rsp = BaseResponse(num, "The current domain does not exist, please create the domain first.")
        return base_rsp, num

    successHost = []
    failedHost = []
    domainPath = os.path.join(TARGETDIR, domain)

    # Check whether the current host exists in the domain.
    for host in host_infos:
        hostPath = os.path.join(domainPath, "hostRecord.txt")
        if os.path.isfile(hostPath):
            isContained = Format.isContainedHostIdInfile(hostPath, host.host_id)
            if isContained:
                print("##########isContained###############")
                failedHost.append(host.host_id)
            else:
                Format.addHostToFile(hostPath, host)
                successHost.append(host.host_id)
        else:
            Format.addHostToFile(hostPath, host)
            successHost.append(host.host_id)

    if len(failedHost) == len(host_infos):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The all host already exists in the administrative scope of the domain.")
        return base_rsp, codeNum

    # Joining together the returned codenum codeMessage
    if len(failedHost) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("host", "add hosts", successHost)
    else:
        codeNum = 202
        codeString = Format.splicErrorString("host", "add hosts", successHost, failedHost)

    # git commit maessage
    if len(host_infos) > 0:
        git_tools = GitTools()
        commit_code = git_tools.gitCommit("Add the host in {} domian, ".format(domain) +
                                "the host including : {}".format(successHost))

    base_rsp = BaseResponse(codeNum, codeString)

    return base_rsp, codeNum


def delete_host_in_domain(body=None):  # noqa: E501
    """delete host in the configuration  domain

    delete the host in the configuration domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: BaseResponse
    """
    if connexion.request.is_json:
        body = HostInfos.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    hostInfos = body.host_infos

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    #  check whether the domain exists
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # Whether the host information added within the current domain is empty while ain exists
    domainPath = os.path.join(TARGETDIR, domain)
    hostPath = os.path.join(domainPath, "hostRecord.txt")
    if not os.path.isfile(hostPath) or (os.path.isfile(hostPath) and os.stat(hostPath).st_size == 0):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." +
                                          "Please add the host information first")
        return base_rsp, codeNum

    # If the input host information is empty, the host information of the whole domain is cleared
    if len(hostInfos) == 0:
        if os.path.isfile(hostPath):
            try:
                os.remove(hostPath)
            except OSError as ex:
                #logging.error("the host delete failed")
                codeNum = 500
                base_rsp = BaseResponse(codeNum, "The host delete failed.")
                return base_rsp, codeNum
            codeNum = 200
            base_rsp = BaseResponse(codeNum, "All hosts are deleted in the current domain.")
            return base_rsp, codeNum

    # If the domain exists, check whether the current input parameter host belongs to the corresponding
    # domain. If the host is in the domain, the host is deleted. If the host is no longer in the domain,
    # the host is added to the failure range
    containedInHost = []
    notContainedInHost = []
    os.umask(0o077)
    for hostInfo in hostInfos:
        hostId = hostInfo.host_id
        isContained = False
        try:
            with open(hostPath, 'r') as d_file:
                lines = d_file.readlines()
                with open(hostPath, 'w') as w_file:
                    for line in lines:
                        line_host_id = json.loads(str(ast.literal_eval(line)).replace("'", "\""))['host_id']
                        if hostId != line_host_id:
                            w_file.write(line)
                        else:
                            isContained = True
        except OSError as err:
            print("OS error: {0}".format(err))
            codeNum = 500
            base_rsp = BaseResponse(codeNum, "OS error: {0}".format(err))
            return base_rsp, codeNum

        if isContained:
            containedInHost.append(hostId)
        else:
            notContainedInHost.append(hostId)

    # All hosts do not belong to the domain
    if len(notContainedInHost) == len(hostInfos):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "All the host does not belong to the domain control, " +
                                         "please enter the host again")
        return base_rsp, codeNum

    # Some hosts belong to domains, and some hosts do not belong to domains.
    if len(notContainedInHost) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("host", "delete", containedInHost)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("host", "delete", containedInHost, notContainedInHost)

    # git commit message
    if len(containedInHost) > 0:
        git_tools = GitTools()
        commit_code = git_tools.gitCommit("Delet the host in {} domian, ".format(domain) +
                                "the host including : {}".format(containedInHost))

    base_rsp = BaseResponse(codeNum, codeString)

    return base_rsp, codeNum


def get_host_by_domain_name(body=None):  # noqa: E501
    """get host by domainName

    get the host information of the configuration domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: List[Host]
    """
    if connexion.request.is_json:
        body = DomainName.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    #  check whether the domain exists
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # The domain exists, but the host information is empty
    domainPath = os.path.join(TARGETDIR, domain)
    hostPath = os.path.join(domainPath, "hostRecord.txt")
    if not os.path.isfile(hostPath) or (os.path.isfile(hostPath) and os.stat(hostPath).st_size == 0):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." +
                                          "Please add the host information first.")
        return base_rsp, codeNum

    # The domain exists, and the host information exists and is not empty
    hostlist = []
    print("hostPath is : {}".format(hostPath))
    try:
        with open(hostPath, 'r') as d_file:
            for line in d_file.readlines():
                json_str = json.loads(line)
                host_json = ast.literal_eval(json_str)
                hostId = host_json["host_id"]
                ip = host_json["ip"]
                ipv6 = host_json["ipv6"]
                host = Host(host_id=hostId, ip=ip, ipv6=ipv6)
                hostlist.append(host)
    except OSError as err:
        print("OS error: {0}".format(err))
        codeNum = 500
        base_rsp = BaseResponse(codeNum, "OS error: {0}".format(err))
        return base_rsp, codeNum

    # Joining together the returned codenum codeMessag
    if len(hostlist) == 0:
        codeNum = 500
        base_rsp = BaseResponse(codeNum, "Some unknown problems.")
        return base_rsp, codeNum
    else:
        print("hostlist is : {}".format(hostlist))
        codeNum = 200
        base_rsp = BaseResponse(codeNum, "Get host info in the domain succeccfully")

    return hostlist
