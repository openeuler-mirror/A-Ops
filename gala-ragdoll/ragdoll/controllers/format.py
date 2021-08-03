import os
import logging
import string
import re
import subprocess
import json

class Format(object):

    @staticmethod
    def isDomainExist(domainName):
        targetDir = "/home/confTrace"
        domainPath = os.path.join(targetDir, domainName)
        if os.path.exists(domainPath):
            return True

        return False

    @staticmethod
    def spliceAllSuccString(obj, operation, succDomain):
        """
        docstring
        """
        codeString = """All {obj} {oper} successfully, {succ} {obj} in total.
                    """.format(obj=obj, oper=operation, succ=len(succDomain))
        return codeString

    @staticmethod
    def splicErrorString(obj, operation, succDomain, failDomain):
        """
        docstring
        """
        codeString = """{succ} {obj} {oper} successfully, \
                        {fail} {obj} {oper} failed. """.format(succ=len(succDomain), \
                        obj=obj, oper=operation, fail=len(failDomain))

        succString = "\n"
        if len(succDomain) > 0:
            succString = "These are successful: "
            for succName in succDomain:
                succString += succName + " "
            succString += "."

        if len(failDomain) > 0:
            failString = "\n These are failed: "
            for failName in failDomain:
                failString += failName + " "
            return codeString + succString + failString

        return codeString + succString

    @staticmethod
    def two_abs_join(abs1, abs2):
        """
        将 绝对路径将两个绝对路径拼接,
        就是将第二个的开路径（windows 的  C， D，E ... Linux 的 /root 最前面的 / 删除掉）
        :param abs1:  为主的路径
        :param abs2:  被拼接的路径
        :return: 拼接后的数值
        """
        # 1. 格式化路径（将路径中的 \\ 改为 \）
        abs2 = os.fspath(abs2)

        # 2. 将路径文件拆分
        abs2 = os.path.splitdrive(abs2)[1]
        # 3. 去掉开头的 斜杠
        abs2 = abs2.strip('\\/') or abs2
        return os.path.abspath(os.path.join(abs1, abs2))

    @staticmethod
    def isContainedInfile(file, content):
        isContained = False
        with open(file, 'r') as d_file:
            for line in d_file.readlines():
                if content in line:
                    isContained = True
                    return isContained

        return isContained

    @staticmethod
    def addHostToFile(file, host):
        info_json = json.dumps(str(host), sort_keys=False, indent=4, separators=(',', ': '))
        with open(file, 'a+') as host_file:
            host_file.write(info_json)
            host_file.write("\n")

    @staticmethod
    def getSubDirFiles(path):
        """
        desc：需要将子目录记录和文件记录到successConf中
        """
        fileRealPathList = []
        fileXPathlist = []
        for root, dirs, files in os.walk(path):
            if len(files) > 0:
                preXpath = root.split('/', 3)[3]
                for d_file in files:
                    xpath = os.path.join(preXpath, d_file)
                    fileXPathlist.append(xpath)
                    realPath = os.path.join(root, d_file)
                    fileRealPathList.append(realPath)

        return fileRealPathList, fileXPathlist

    @staticmethod
    def isHostInDomain(domainName):
        """
        desc: 查询domain域内是否已经配置host信息
        """
        isHostInDomain = False
        domainPath = os.path.join("/home/confTrace", domainName)
        hostPath = os.path.join(domainPath, "hostRecord.txt")
        if os.path.isfile(hostPath):
            isHostInDomain = True

        return isHostInDomain

    @staticmethod
    def isHostIdExist(hostPath, hostId):
        """
        desc: 查询hostId是否存在当前的host域管理范围内
        """
        isHostIdExist = False
        if os.path.isfile(hostPath) and os.stat(hostPath).st_size > 0:
            with open(hostPath) as h_file:
                for line in h_file.readlines():
                    if hostId in line:
                        isHostIdExist = True
                        break

        return isHostIdExist

    @staticmethod
    def is_exists_file(d_file):
        if os.path.exists(d_file):
            return True
        if not os.path.exists(d_file):
            if os.path.islink(d_file):
                logging.debug("file: %s is a symlink, skipped!", d_file)
                return False
            logging.error("file: %s does not exist.", d_file)
            return False

    @staticmethod
    def get_file_content_by_readlines(d_file) -> []:
        """
        desc: remove empty lines and comments from d_file
        """
        res = []
        with open(d_file, 'r') as s_f:
            lines = s_f.readlines()
            for line in lines:
                tmp = line.strip()
                if not len(tmp) or tmp.startswith("#"):
                    continue
                res.append(line)
        return res

    @staticmethod
    def get_file_content_by_read(d_file):
        """
        desc: return a string after read the d_file
        """
        with open(d_file, 'r') as s_f:
            lines = s_f.read()
        return lines

    @staticmethod
    def rsplit(_str, seps):
        """
        Splits _str by the first sep in seps that is found from the right side.
        Returns a tuple without the separator.
        """
        for idx, ch in enumerate(reversed(_str)):
            if ch in seps:
                return _str[0:-idx - 1], _str[-idx:]

    @staticmethod
    def _arch_sep(package_string):
        """
        Helper method for finding if arch separator is '.' or '-'

        Args:
            package_string (str): dash separated package string such as 'bash-4.2.39-3.el7'.

        Returns:
            str: arch separator
        """
        return '.' if package_string.rfind('.') > package_string.rfind('-') else '-'

    @staticmethod
    def set_file_content_by_path(content, path):
        res = 0
        if os.path.exists(path):
            with open(path, 'w+') as d_file:
                for d_cont in content:
                    d_file.write(d_cont)
                    d_file.write("\n")
            res = 1
        return res
