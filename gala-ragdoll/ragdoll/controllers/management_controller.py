import connexion
import six
import os
import shutil
import json

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
from ragdoll.models.manage_conf import ManageConf
from ragdoll.utils.conf_tools import ConfTools
from ragdoll.utils.git_tools import GitTools
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.object_parse import ObjectParse
from ragdoll.analy.openEuler_repo import OpenEulerRepo
from ragdoll.parses.ini_parse import IniJsonParser

TARGETDIR = "/home/confTrace"


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

    # 提前check domain是否存在
    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist, please create the domain first.")
        return base_rsp

    # check conf_files是否为空
    if len(conf_files) == 0:
        base_rsp = BaseResponse(400, "The path of file can't be empty")
        return base_rsp

    # 整理所有的conf_files，判断contents是否为空，如果为空，则调用查询实际配置接口，如果不为空，则直接进行转换。
    # content和host_id为二选一，若都为空，则返回有非法输入
    contents_list_null = []
    contents_list_non_null = []
    for d_conf in conf_files:
        if d_conf.contents:
            contents_list_non_null.append(d_conf)
        elif d_conf.host_id:
            contents_list_null.append(d_conf)
        else:
            base_rsp = BaseResponse(400, "Invalid input exists.")
            return base_rsp

    successConf = []
    failedConf = []
    object_parse = ObjectParse()
    yang_module = YangModule()
    conf_tools = ConfTools()
    # content不为空场景, 直接进行解析和转换
    for d_conf in contents_list_non_null:
        content_string = object_parse.parse_content_to_json(d_conf.file_path, d_conf.contents)
        # 在domian域中创建配置和期望值
        feature_path = yang_module.get_feature_by_real_path(domain, d_conf.file_path)
        result = conf_tools.wirteFileInPath(feature_path, content_string + '\n')
        if result:
            successConf.append(d_conf.file_path)
        else:
            failedConf.append(d_conf.file_path)

    # content为空的场景
    for d_conf in contents_list_null:
        # 调用查询真实配置的接口，获取真实配置
        print("d_conf is : {}".format(d_conf))
        file_path = d_conf.file_path
        host = d_conf.host_id
        if os.path.exists(file_path):
            content = Format.get_file_content_by_read(file_path)
            content_string = object_parse.parse_content_to_json(file_path, content)
            # 在domian域中创建配置和期望值
            feature_path = yang_module.get_feature_by_real_path(domain, file_path)
            result = conf_tools.wirteFileInPath(feature_path, content_string)
            if result:
                successConf.append(d_conf.file_path)
            else:
                failedConf.append(d_conf.file_path)
        else:
            failedConf.append("file_path")

    # 提交commit记录
    if len(successConf) > 0:
        git_tools = GitTools()
        succ_conf = ""
        for d_conf in successConf:
            succ_conf = succ_conf + d_conf + " "
        commit_code = git_tools.gitCommit("Add the conf in {} domian, the path including : {}".format(domain, succ_conf))

    # 拼接返回的codenum codeMessage
    if len(failedConf) == 0:
        codeNum = 200
        codeString = Format.spliceAllSuccString("confs", "add management conf", successConf)
    else:
        codeNum = 400
        codeString = Format.splicErrorString("confs", "add management conf", successConf, failedConf)

    base_rsp = BaseResponse(codeNum, codeString)
    # logging.info('add management conf in {domain}'.format(domain=domain))

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

    # 需要提前check domain是否存在
    domain = body.domain_name
    print("body is : {}".format(body))
    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist")
        return base_rsp
    
    # 需要提前判断path输入是否为空  -》 后续不应该在此判断
    conf_files = body.conf_files
    if len(conf_files) == 0:
        base_rsp = BaseResponse(400, "The conf_files path can't be empty")
        return base_rsp

    # 用来记录成功与失败的conf
    successConf = []
    failedConf = []

    # 判断path在域内是否存在，且path存在两种可能：(1)xpath路径 （2）配置项
    domain_path = os.path.join("/home/confTrace", domain)
    print("conf_files is : {}".format(conf_files))

    yang_modules = YangModule()
    module_lists = yang_modules._module_list
    if len(module_lists) == 0:
        base_rsp = BaseResponse(400, "The yang module does not exist")
        return base_rsp

    file_path_list = yang_modules.getFilePathInModdule(module_lists)
    print("module_lists is : {}".format(module_lists))
    for conf in conf_files:
        module = yang_modules.getModuleByFilePath(conf.file_path)
        features = yang_modules.getFeatureInModule(module)
        for d_fea in features:
            domain_path = os.path.join(domain_path, d_fea)
        print("domain_path is : {}".format(domain_path))

        if os.path.isfile(domain_path):
            print("it's a normal file")
            try:
                os.remove(domain_path)
            except OSError as ex:
                logging.error("the path remove failed")
                break
            successConf.append(conf.file_path)
        else:
            failedConf.append(conf.path)

    # 提交commit记录
    if len(successConf) > 0:
        git_tools = GitTools()
        succ_conf = ""
        for d_conf in successConf:
            succ_conf = succ_conf + d_conf + " "
        commit_code = git_tools.gitCommit("delete the conf in {} domian, the path including : {}".format(domain, succ_conf))

    # 拼接返回的codenum codeMessage
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
    
    # 需要提前check domain是否存在
    domain = body.domain_name
    isExist = Format.isDomainExist(domain)
    if not isExist:
        base_rsp = BaseResponse(400, "The current domain does not exist")
        return base_rsp, 400

    # 对返回参数进行初始赋值
    expected_conf_lists = ConfFiles(domain_name = domain,
                                    conf_files = [])

    # 获得 domain下的path
    domainPath = os.path.join(TARGETDIR, domain)
    print("########## domainPath is : {} ########## ".format(domainPath))

    # 路径下存在文件时即判断为配置项的path
    for root, dirs, files in os.walk(domainPath):
        # domain下还含有host缓存文件，所以需要增加对于root的层次判断
        if len(files) > 0 and len(root.split('/')) > 3:
            if "hostRecord.txt" in files:
                continue
            confPath = root.split('/', 3)[3]
            for d_file in files:
                
                d_file_path = os.path.join(root, d_file)
                contents = Format.get_file_content_by_read(d_file_path)

                feature = os.path.join(root.split('/')[-1], d_file)
                yang_modules = YangModule()
                d_module = yang_modules.getModuleByFeature(feature)
                file_lists = yang_modules.getFilePathInModdule(yang_modules._module_list)
                file_path = file_lists.get(d_module.name())

                conf = ConfFile(file_path = file_path, contents = contents)
                expected_conf_lists.conf_files.append(conf)
    print("expected_conf_lists is :{}".format(expected_conf_lists))

    if len(expected_conf_lists.domain_name) > 0:
        base_rsp = BaseResponse(200, "Get management configuration items and expected values in the domain succeccfully")
    else:
        base_rsp = BaseResponse(400, "The file is Null in this domain")

    return expected_conf_lists
