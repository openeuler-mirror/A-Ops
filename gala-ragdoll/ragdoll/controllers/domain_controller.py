import connexion
import six
import os
import shutil
import logging

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.domain import Domain  # noqa: E501
from ragdoll import util
from ragdoll.controllers.format import Format
from ragdoll.utils.git_tools import GitTools

TARGETDIR = GitTools().target_dir

# logging.basicConfig(filename='log.log',
#                     format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S %p',
#                     level=10)

def create_domain(body=None):  # noqa: E501
    """create domain

    create domain # noqa: E501

    :param body: domain info
    :type body: list | bytes

    :rtype: BaseResponse
    """
    if connexion.request.is_json:
        body = [Domain.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501

    if len(body) == 0:
        base_rsp = BaseResponse(400, "The entered domian is empty")
        return base_rsp

    successDomain = []
    failedDomain = []

    for domain in body:
        tempDomainName = domain.domain_name
        isVerFication = Format.domainCheck(tempDomainName)
        if not isVerFication:
            codeNum = 400
            codeString = "Interface input parameters verification failed. Please check the input parameters."
            base_rsp = BaseResponse(codeNum, codeString)
            return base_rsp, codeNum
        isExist = Format.isDomainExist(tempDomainName)
        if isExist:
            failedDomain.append(tempDomainName)
        else:
            successDomain.append(tempDomainName)
            domainPath = os.path.join(TARGETDIR, tempDomainName)
            os.mkdir(domainPath)

    if len(failedDomain) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("domain", "created", successDomain)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("domain", "created", successDomain, failedDomain)

    base_rsp = BaseResponse(codeNum, codeString)

    return base_rsp, codeNum


def delete_domain(domainName):  # noqa: E501
    """delete domain

    delete domain # noqa: E501

    :param domainName: the domain that needs to be deleted
    :type domainName: List[str]

    :rtype: BaseResponse
    """
    if len(domainName) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The entered domian is empty")
        return base_rsp, codeNum

    successDomain = []
    failedDomain = []

    for tempDomainName in domainName:
        isExist = Format.isDomainExist(tempDomainName)
        if isExist:
            domainPath = os.path.join(TARGETDIR, tempDomainName)
            successDomain.append(tempDomainName)
            shutil.rmtree(domainPath)
        else:
            failedDomain.append(tempDomainName)

    if len(failedDomain) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("domain", "delete", successDomain)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("domain", "delete", successDomain, failedDomain)

    base_rsp = BaseResponse(codeNum, codeString)
    return base_rsp, codeNum


def query_domain():  # noqa: E501
    """
    query the list of all configuration domain # noqa: E501
    :rtype: List[Domain]
    """
    domain_list = []
    cmd = "ls {}".format(TARGETDIR)
    gitTools = GitTools()
    ls_res = gitTools.run_shell_return_output(cmd).decode()
    ll_list = ls_res.split('\n')
    for d_ll in ll_list:
        if d_ll:
            domain = Domain(domain_name = d_ll)
            domain_list.append(domain)

    if len(domain_list) > 0:
        codeNum = 200
    else:
        codeNum = 400
        codeString = "The current configuration domain is empty. Add a configuration domain first"
        base_rsp = BaseResponse(codeNum, codeString)
        return base_rsp, codeNum

    return domain_list, codeNum
