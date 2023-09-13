import connexion
import six
import os
import shutil
import json
import requests

from ragdoll.log.log import LOGGER
from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.conf import Conf
from ragdoll.models.confs import Confs
from ragdoll.models.conf_file import ConfFile
from ragdoll.models.conf_files import ConfFiles
from ragdoll.models.git_log_message import GitLogMessage
from ragdoll.models.conf_base_info import ConfBaseInfo
from ragdoll.models.domain_manage_conf import DomainManageConf  # noqa: E501
from ragdoll.models.excepted_conf_info import ExceptedConfInfo
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.manage_conf import ManageConf
from ragdoll.models.manage_confs import ManageConfs
from ragdoll import util
from ragdoll.controllers.format import Format
from ragdoll.utils.conf_tools import ConfTools
from ragdoll.utils.git_tools import GitTools
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.object_parse import ObjectParse


TARGETDIR = GitTools().target_dir


def add_management_confs_in_domain(body=None):  # noqa: E501
    """add management configuration items and expected values in the domain

    add management configuration items and expected values in the domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: BaseResponse
    """
    if connexion.request.is_json:
        body = Confs.from_dict(connexion.request.get_json())  # noqa: E501

    domain = body.domain_name
    conf_files = body.conf_files

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    # check whether the domain exists
    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # check whether the conf_files is null
    if len(conf_files) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The path of file can't be empty")
        return base_rsp, codeNum

    # Check all conf_files and check whether contents is empty. If so, the query actual configuration 
    # interface is called. If not, the conversion is performed directly.
    # Content and host_id can be set to either content or host_id. 
    # If they are both empty, invalid input is returned.
    contents_list_null = []
    contents_list_non_null = []
    for d_conf in conf_files:
        if d_conf.contents:
            contents_list_non_null.append(d_conf)
        elif d_conf.host_id:
            contents_list_null.append(d_conf)
        else:
            codeNum = 400
            base_rsp = BaseResponse(codeNum, "The input parameters are not compliant, " +
                                             "please check the input parameters.")
            return base_rsp, codeNum

    successConf = []
    failedConf = []
    object_parse = ObjectParse()
    yang_module = YangModule()
    conf_tools = ConfTools()
    # Content is not an empty scene and is directly analyed and parsed
    if len(contents_list_non_null) > 0:
        for d_conf in contents_list_non_null:
            if not d_conf.contents.strip():
                codeNum = 400
                base_rsp = BaseResponse(codeNum, "The input parameters are not compliant, " +
                                                 "please check the input parameters.")
                return base_rsp, codeNum
            content_string = object_parse.parse_conf_to_json(d_conf.file_path, d_conf.contents)
            if not content_string or not json.loads(content_string):
                failedConf.append(d_conf.file_path)
            else:
                # create the file and expected value in domain
                feature_path = yang_module.get_feature_by_real_path(domain, d_conf.file_path)
                result = conf_tools.wirteFileInPath(feature_path, content_string + '\n')
                if result:
                    successConf.append(d_conf.file_path)
                else:
                    failedConf.append(d_conf.file_path)

    # content is empty
    if len(contents_list_null) > 0:
        # get the real conf in host
        print("############## get the real conf in host ##############")
        get_real_conf_body = {}
        get_real_conf_body_info = []
        print("contents_list_null is : {}".format(contents_list_null))
        exist_host = dict()
        for d_conf in contents_list_null:
            host_id = int(d_conf.host_id)
            if host_id in exist_host:
                exist_host[host_id].append(d_conf.file_path)
            else:
                conf_list = list()
                conf_list.append(d_conf.file_path)
                exist_host[host_id] = conf_list
        for k,v in exist_host:
            confs = dict()
            confs["host_id"] = k
            confs["config_list"] = v
            get_real_conf_body_info.append(confs)

        get_real_conf_body["infos"] = get_real_conf_body_info

        url = conf_tools.load_url_by_conf().get("collect_url")
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(get_real_conf_body), headers=headers)  # post request
        
        response_code = json.loads(response.text).get("code")
        if response_code == None:
            codeNum = 500
            codeString = "Failed to obtain the actual configuration, please check the interface of conf/collect."
            base_rsp = BaseResponse(codeNum, codeString)
            return base_rsp, codeNum

        if (response_code != "200") and (response_code != "206"):
            codeNum = 500
            codeString = "Failed to obtain the actual configuration, please check the file exists."
            base_rsp = BaseResponse(codeNum, codeString)
            return base_rsp, codeNum

        reps = json.loads(response.text).get("data")
        if not reps or len(reps) == 0:
            codeNum = 500
            codeString = "Failed to obtain the actual configuration, please check the host info for conf/collect."
            base_rsp = BaseResponse(codeNum, codeString)
            return base_rsp, codeNum

        for d_res in reps:
            failedlist = d_res.get("fail_files")
            if len(failedlist) > 0:
                for d_failed in failedlist:
                    failedConf.append(d_failed)
                continue
            d_res_infos = d_res.get("infos")
            for d_file in d_res_infos:
                file_path = d_file.get("path")
                content = d_file.get("content")
                content_string = object_parse.parse_conf_to_json(file_path, content)
                # create the file and expected value in domain
                if not content_string or not json.loads(content_string):
                    failedConf.append(file_path)
                else:
                    feature_path = yang_module.get_feature_by_real_path(domain, file_path)
                    result = conf_tools.wirteFileInPath(feature_path, content_string + '\n')
                    if result:
                        successConf.append(file_path)
                    else:
                        failedConf.append(file_path)

    # git commit message
    if len(successConf) > 0:
        git_tools = GitTools()
        succ_conf = ""
        for d_conf in successConf:
            succ_conf = succ_conf + d_conf + " "
        commit_code = git_tools.gitCommit("Add the conf in {} domian, ".format(domain) + 
                                          "the path including : {}".format(succ_conf))

    # Joinin together the returned codenum and codeMessage
    print("*******************************************")
    print("successConf is : {}".format(successConf))
    print("failedConf is : {}".format(failedConf))
    if len(successConf) == 0:
        codeNum = 400
        codeString = "All configurations failed to be added."
    elif len(failedConf) > 0:
        codeNum = 206
        codeString = Format.splicErrorString("confs", "add management conf", successConf, failedConf)
    else:
        codeNum = 200
        codeString = Format.spliceAllSuccString("confs", "add management conf", successConf)

    base_rsp = BaseResponse(codeNum, codeString)

    return base_rsp, codeNum

def upload_management_confs_in_domain(file=None):  # noqa: E501
    """upload management configuration items and expected values in the domain

    upload management configuration items and expected values in the domain # noqa: E501

    :param body: file info
    :type body: FileStorage

    :rtype: BaseResponse
    """
    filePath = connexion.request.form.get("filePath")
    domainName = connexion.request.form.get("domainName")

    # check the input domainName
    checkRes = Format.domainCheck(domainName)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    # check whether the domainName exists
    isExist = Format.isDomainExist(domainName)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist, please create the domain first.")
        return base_rsp, codeNum

    # check whether the file is null
    if file is None:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The file of conf can't be empty")
        return base_rsp, codeNum

    # check whether the conf is null
    if filePath is None:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The conf body of conf can't be empty")
        return base_rsp, codeNum

    successConf = []
    failedConf = []
    object_parse = ObjectParse()
    yang_module = YangModule()
    conf_tools = ConfTools()

    # content is file
    if file:
        if not filePath.strip():
            codeNum = 400
            base_rsp = BaseResponse(codeNum, "The input parameters are not compliant, " +
                                    "please check the input parameters.")
            return base_rsp, codeNum
        try:
            content = file.read().decode("utf-8")
            line_content = content + "\n"
        except OSError as err:
            LOGGER.info("OS error: {}".format(err))
            codeNum = 500
            base_rsp = BaseResponse(codeNum, "OS error: {0}".format(err))
            return base_rsp, codeNum

        content_string = object_parse.parse_conf_to_json(filePath, line_content)
        if not content_string or not json.loads(content_string):
            failedConf.append(filePath)
        else:
            # create the file and expected value in domain
            feature_path = yang_module.get_feature_by_real_path(domainName, filePath)
            result = conf_tools.wirteFileInPath(feature_path, content_string + '\n')
            if result:
                successConf.append(filePath)
            else:
                failedConf.append(filePath)

    # git commit message
    if len(successConf) > 0:
        git_tools = GitTools()
        succ_conf = ""
        for d_conf in successConf:
            succ_conf = succ_conf + d_conf + " "
        commit_code = git_tools.gitCommit("Add the conf in {} domian, ".format(domainName) +
                                          "the path including : {}".format(succ_conf))

    # Joinin together the returned codenum and codeMessage
    print("*******************************************")
    print("successConf is : {}".format(successConf))
    print("failedConf is : {}".format(failedConf))
    if len(successConf) == 0:
        codeNum = 400
        codeString = "All configurations failed to be added."
    elif len(failedConf) > 0:
        codeNum = 206
        codeString = Format.splicErrorString("confs", "add management conf", successConf, failedConf)
    else:
        codeNum = 200
        codeString = Format.spliceAllSuccString("confs", "add management conf", successConf)

    base_rsp = BaseResponse(codeNum, codeString)

    return base_rsp, codeNum

def delete_management_confs_in_domain(body=None):  # noqa: E501
    """delete management configuration items and expected values in the domain

    delete management configuration items and expected values in the domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: BaseResponse
    """
    if connexion.request.is_json:
        body = ManageConfs.from_dict(connexion.request.get_json())  # noqa: E501

    #  check whether the domain exists
    domain = body.domain_name

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    isExist = Format.isDomainExist(domain)
    if not isExist:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The current domain does not exist")
        return base_rsp, codeNum
    
    # Check whether path is null in advance
    conf_files = body.conf_files
    if len(conf_files) == 0:
        codeNum = 400
        base_rsp = BaseResponse(codeNum, "The conf_files path can't be empty")
        return base_rsp, codeNum

    # Conf to record successes and failures
    successConf = []
    failedConf = []

    # Check whether path exists in the domain. There are two possible paths :
    # (1)xpath path
    # (2) configuration item
    domain_path = os.path.join(TARGETDIR, domain)
    print("conf_files is : {}".format(conf_files))

    yang_modules = YangModule()
    module_lists = yang_modules.module_list
    if len(module_lists) == 0:
        base_rsp = BaseResponse(400, "The yang module does not exist")
        return base_rsp

    file_path_list = yang_modules.getFilePathInModdule(module_lists)
    print("module_lists is : {}".format(module_lists))
    for conf in conf_files:
        module = yang_modules.getModuleByFilePath(conf.file_path)
        features = yang_modules.getFeatureInModule(module)
        features_path = os.path.join(domain_path, "/".join(features))
        print("domain_path is : {}".format(domain_path))

        if os.path.isfile(features_path):
            print("it's a normal file")
            try:
                os.remove(features_path)
            except OSError as ex:
                #logging.error("the path remove failed")
                break
            successConf.append(conf.file_path)
        else:
            failedConf.append(conf.file_path)

    # git commit message
    if len(successConf) > 0:
        git_tools = GitTools()
        succ_conf = ""
        for d_conf in successConf:
            succ_conf = succ_conf + d_conf + " "
        commit_code = git_tools.gitCommit("delete the conf in {} domian, ".format(domain) + 
                                          "the path including : {}".format(succ_conf))

    # Joinin together the returned codenum and codeMessage
    if len(failedConf) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("confs", "delete management conf", successConf)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("confs", "delete management conf", successConf, failedConf)
        codeString += "\n The reason for the failure is: these paths do not exist."
    base_rsp = BaseResponse(codeNum, codeString)
    # logging.info('delete management conf in {domain}'.format(domain=domain))

    return base_rsp, codeNum


def get_management_confs_in_domain(body=None):  # noqa: E501
    """get management configuration items and expected values in the domain

    get management configuration items and expected values in the domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: ConfFiles
    """
    if connexion.request.is_json:
        body = DomainName.from_dict(connexion.request.get_json())  # noqa: E501

    # Check whether the domain exists
    domain = body.domain_name

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist")
        return base_rsp, 400

    # The parameters of the initial return value assignment
    expected_conf_lists = ConfFiles(domain_name = domain,
                                    conf_files = [])

    # get the path in domain
    domainPath = os.path.join(TARGETDIR, domain)

    # When there is a file path is the path of judgment for the configuration items
    for root, dirs, files in os.walk(domainPath):
        if len(files) > 0 and len(root.split('/')) > 3:
            if "hostRecord.txt" in files:
                continue
            for d_file in files:
                d_file_path = os.path.join(root, d_file)
                contents = Format.get_file_content_by_read(d_file_path)
                feature = os.path.join(root.split('/')[-1], d_file)
                yang_modules = YangModule()
                d_module = yang_modules.getModuleByFeature(feature)
                file_lists = yang_modules.getFilePathInModdule(yang_modules.module_list)
                file_path = file_lists.get(d_module.name()).split(":")[-1]

                conf = ConfFile(file_path = file_path, contents = contents)
                expected_conf_lists.conf_files.append(conf)
    print("expected_conf_lists is :{}".format(expected_conf_lists))

    if len(expected_conf_lists.domain_name) > 0:
        base_rsp = BaseResponse(200, "Get management configuration items and expected " + 
                                     "values in the domain succeccfully")
    else:
        base_rsp = BaseResponse(400, "The file is Null in this domain")

    return expected_conf_lists


def query_changelog_of_management_confs_in_domain(body=None):  # noqa: E501
    """query the change log of management config in domain

    query the change log of management config in domain # noqa: E501

    :param body: domain info
    :type body: dict | bytes

    :rtype: ExceptedConfInfo
    """
    if connexion.request.is_json:
        body = ManageConfs.from_dict(connexion.request.get_json())  # noqa: E501

    #  check whether the domain exists
    domain = body.domain_name
    print("body is : {}".format(body))

    # check the input domain
    checkRes = Format.domainCheck(domain)
    if not checkRes:
        num = 400
        base_rsp = BaseResponse(num, "Failed to verify the input parameter, please check the input parameters.")
        return base_rsp, num

    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist")
        return base_rsp

    # Check whether path is empty in advance. If path is empty, the configuration in the 
    # entire domain is queried. Otherwise, the historical records of the specified file are queried.
    conf_files = body.conf_files
    print("conf_files is : {}".format(conf_files))
    print("conf_files's type is : {}".format(type(conf_files)))
    conf_files_list = []
    if conf_files:
        for d_conf in conf_files:
            print("d_conf is : {}".format(d_conf))
            print("d_conf type is : {}".format(type(d_conf)))
            conf_files_list.append(d_conf.file_path)
    success_conf = []
    failed_conf = []
    domain_path = os.path.join(TARGETDIR, domain)
    expected_conf_lists = ExceptedConfInfo(domain_name = domain,
                                           conf_base_infos = [])
    yang_modules = YangModule()
    for root, dirs, files in os.walk(domain_path):
        conf_base_infos = []
        if len(files) > 0 and len(root.split('/')) > 3:
            if "hostRecord.txt" in files:
                continue
            confPath = root.split('/', 3)[3]
            for d_file in files:
                feature = os.path.join(root.split('/')[-1], d_file)
                d_module = yang_modules.getModuleByFeature(feature)
                file_lists = yang_modules.getFilePathInModdule(yang_modules.module_list)
                file_path = file_lists.get(d_module.name()).split(":")[-1]
                if (conf_files_list) and (file_path not in conf_files_list):
                    continue
                d_file_path = os.path.join(root, d_file)
                expectedValue = Format.get_file_content_by_read(d_file_path)
                git_tools = GitTools()
                gitMessage = git_tools.getLogMessageByPath(d_file_path)
                if gitMessage and expectedValue:
                    success_conf.append(file_path)
                else:
                    failed_conf.append(file_path)
                conf_base_info = ConfBaseInfo(file_path = file_path,
                                              expected_contents = expectedValue,
                                              change_log = gitMessage)
                expected_conf_lists.conf_base_infos.append(conf_base_info)

    print("########################## expetedConfInfo ####################")
    print("expected_conf_lists is : {}".format(expected_conf_lists))
    print("########################## expetedConfInfo  end ####################")

    if len(success_conf) == 0:
        codeNum = 500
        base_rsp = BaseResponse(codeNum, "Faled to uery the changelog of the configure in the domain.")
        return base_rsp, codeNum
    if len(failed_conf) > 0:
        codeNum = 400
    else:
        codeNum = 200

    return expected_conf_lists, codeNum
