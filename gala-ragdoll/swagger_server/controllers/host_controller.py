import connexion
import six
import os
import json

from swagger_server.models.base_response import BaseResponse  # noqa: E501
from swagger_server.models.domain_name import DomainName  # noqa: E501
from swagger_server.models.host import Host  # noqa: E501
from swagger_server.models.host_infos import HostInfos  # noqa: E501
from swagger_server import util
from swagger_server.models.host import Host
from swagger_server.controllers.format import Format


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

    # 确认输入的host不为空 -》 后续可删除
    if len(host_infos) == 0:
        base_rsp = BaseResponse(400, "The entered host is empty")
        return base_rsp

    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist, please create the domain first.")
        return base_rsp

    # 用来记录成功与失败的Host
    successHost = []
    failedHost = []
    domainPath = os.path.join("/home/confTrace", domain)

    # 判断当前host是否已经存在domain域的管理范围内：
    for host in host_infos:
        hostPath = os.path.join(domainPath, "hostRecord.txt")
        if os.path.isfile(hostPath):
            isContained = Format.isContainedInfile(hostPath, host.host_id)

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

    # 拼接返回的codenum codeMessage
    if len(failedHost) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("host", "add hosts", successHost)
    else:
        codeNum = 202
        codeString = Format.splicErrorString("host", "add hosts", successHost, failedHost)

    base_rsp = BaseResponse(codeNum, codeString)
    # logging.info('add host in {domain}'.format(domain=domain))

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

    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # domain存在，当前domain域内添加的host信息是否为空
    domainPath = os.path.join("/home/confTrace", domain)
    hostPath = os.path.join(domainPath, "hostRecord.txt")
    if not os.path.isfile(hostPath) or (os.path.isfile(hostPath) and os.stat(hostPath).st_size == 0):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." +  
                                          "Please add the host information first")
        return base_rsp, codeNum

    # domain存在，输入的host信息为空，则清除整个domain域的host信息
    if len(hostInfos) == 0:
        if os.path.isfile(hostPath):
            try:
                os.remove(hostPath)
            except OSError as ex:
                logging.error("the host delete failed")
                codeNum = 500
                base_rsp = BaseResponse(codeNum, "The host delete failed.")
                return base_rsp, codeNum

    # domain存在，检测当前入参host是否归属在对应的domain内， 如果在domain内则删除，不再则不处理，添加到失败范围内
    containedInHost = []
    notContainedInHost = []
    for hostInfo in hostInfos:
        hostId = hostInfo.host_id
        isContained = False
        try:
            with open(hostPath, 'r') as d_file:
                lines = d_file.readlines()
                with open(hostPath, 'w') as w_file:
                    for line in lines:
                        if hostId not in line:
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

    # 所有的host均不属于domain
    if len(notContainedInHost) == len(hostInfos):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "All the host does not belong to the domain control, " + 
                                         "please enter the host again")
        return base_rsp, codeNum

    # 部分host属于domain， 部分host不属于domain
    if len(notContainedInHost) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("host", "delete", containedInHost)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("host", "delete", containedInHost, notContainedInHost)

    base_rsp = BaseResponse(codeNum, codeString)
    # logging.info('delete host')

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

    # 需要提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # domain存在，host信息是否为空
    domainPath = os.path.join("/home/confTrace", domain)
    hostPath = os.path.join(domainPath, "hostRecord.txt")
    if not os.path.isfile(hostPath) or (os.path.isfile(hostPath) and os.stat(hostPath).st_size == 0):
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The host information is not set in the current domain." +  
                                          "Please add the host information first")
        return base_rsp, codeNum

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    # domain存在，host信息也存在, 且不为空
    hostlist = []
    print("hostPath is : {}".format(hostPath))
    try:
        with open(hostPath, 'r') as d_file:
            for line in d_file.readlines():
                #每个字段之间采用",\n"作为间隔，最后一个字段需要去除尾部的"}"和首部的空格
                hostInfo = line.split(",\\n")
                # ip和host的string为: " 'xxxx'"，所以采取截取[2:-1]来获取实际值
                hostId = hostInfo[0].split(":")[1][2:-1]
                ip = hostInfo[1].split(":")[1][2:-1]
                #ipv6的string为：' None}"\n'
                ipv6 = hostInfo[2].split(":")[1][1:-3]
                host = Host(host_id=hostId, ip=ip, ipv6=ipv6)
                hostlist.append(host)
    except OSError as err:
        print("OS error: {0}".format(err))
        codeNum = 500
        base_rsp = BaseResponse(codeNum, "OS error: {0}".format(err))
        return base_rsp, codeNum

    # 拼接返回的codenum codeMessage
    if len(hostlist) == 0:
        codeNum = 500
        base_rsp = BaseResponse(codeNum, "Some unknown problems.")
        return base_rsp, codeNum
    else:
        print("hostlist is : {}".format(hostlist))
        codeNum = 200
        base_rsp = BaseResponse(codeNum, "Get host info in the domain succeccfully")

    return hostlist
