import connexion
import six
import os
import shutil
import logging

from swagger_server.models.base_response import BaseResponse  # noqa: E501
from swagger_server.models.domain import Domain  # noqa: E501
from swagger_server import util
from swagger_server.controllers.format import Format
from swagger_server.utils.git_tools import GitTools

targetDir = "/home/confTrace"

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
        tempDomainName = domain._domain_name
        isExist = Format.isDomainExist(tempDomainName)
        if isExist:
            failedDomain.append(tempDomainName)
        else:
            successDomain.append(tempDomainName)
            domainPath = os.path.join(targetDir, tempDomainName)
            os.mkdir(domainPath)

    if len(failedDomain) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("domain", "created", successDomain)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("domain", "created", successDomain, failedDomain)

    base_rsp = BaseResponse(codeNum, codeString)
    logging.info('domain created successfully, including {}'.format(successDomain))

    return base_rsp, codeNum


def delete_domain(domainName):  # noqa: E501
    """delete domain

    delete domain # noqa: E501

    :param domainName: the domain that needs to be deleted
    :type domainName: List[str]

    :rtype: BaseResponse
    """
    if len(domainName) == 0:
        base_rsp = BaseResponse(400, "The entered domian is empty")
        return base_rsp

    targetDir = "/home/confTrace"
    successDomain = []
    failedDomain = []

    print("domainName is : {}".format(domainName))
    for tempDomainName in domainName:
        domainPath = os.path.join(targetDir, tempDomainName)
        isExist = Format.isDomainExist(domainPath)
        print("isExist is : {}".format(isExist))
        if isExist:
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
    logging.info('delete domain')

    return base_rsp, codeNum
