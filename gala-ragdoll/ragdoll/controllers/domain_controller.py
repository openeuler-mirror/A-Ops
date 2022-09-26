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
        base_rsp = BaseResponse(400, "The input domain cannot be empty, please check the domain.")
        return base_rsp

    successDomain = []
    failedDomain = []

    for domain in body:
        tempDomainName = domain.domain_name
        checkRes = Format.domainCheck(tempDomainName)
        isExist = Format.isDomainExist(tempDomainName)
        if isExist or not checkRes:
            failedDomain.append(tempDomainName)
        else:
            successDomain.append(tempDomainName)
            domainPath = os.path.join(TARGETDIR, tempDomainName)
            os.umask(0o077)
            os.mkdir(domainPath)

    if len(failedDomain) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("domain", "created", successDomain)
    else:
        codeNum = 400
        if len(body) == 1:
            if isExist:
                codeString = "domain {} create failed because it has been existed.".format(failedDomain[0])
            elif not checkRes:
                codeString = "domain {} create failed because format is incorrect.".format(failedDomain[0])
        else:
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
        checkRes = Format.domainCheck(tempDomainName)
        isExist = Format.isDomainExist(tempDomainName)
        if checkRes and isExist:
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

    return domain_list, 200
