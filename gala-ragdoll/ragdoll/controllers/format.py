import os
import logging
import string
import re
import subprocess
import json
import configparser
import ast

CONFIG = "/etc/ragdoll/gala-ragdoll.conf"

class Format(object):

    @staticmethod
    def domainCheck(domainName):
        res = True
        if not re.match(r"^[A-Za-z0-9_\.-]*$", domainName) or domainName == "" or len(domainName) > 255:
            return False
        return res

    @staticmethod
    def isDomainExist(domainName):
        TARGETDIR = Format.get_git_dir()
        domainPath = os.path.join(TARGETDIR, domainName)
        if os.path.exists(domainPath):
            return True

        return False

    @staticmethod
    def spliceAllSuccString(obj, operation, succDomain):
        """
        docstring
        """
        codeString = "All {obj} {oper} successfully, {succ} {obj} in total.".format( \
            obj=obj, oper=operation, succ=len(succDomain))
        return codeString

    @staticmethod
    def splicErrorString(obj, operation, succDomain, failDomain):
        """
        docstring
        """
        codeString = "{succ} {obj} {oper} successfully, {fail} {obj} {oper} failed.".format( \
            succ=len(succDomain), obj=obj, oper=operation, fail=len(failDomain))

        succString = "\n"
        if len(succDomain) > 0:
            succString = "These are successful: "
            for succName in succDomain:
                succString += succName + " "
            succString += "."

        if len(failDomain) > 0:
            failString = "These are failed: "
            for failName in failDomain:
                failString += failName + " "
            return codeString + succString + failString

        return codeString + succString

    @staticmethod
    def two_abs_join(abs1, abs2):
        """
        Absolute path Joins two absolute paths together
        :param abs1:  main path
        :param abs2:  the spliced path
        :return: together the path
        """
        # 1. Format path (change \\ in path to \)
        abs2 = os.fspath(abs2)

        # 2. Split the path file
        abs2 = os.path.splitdrive(abs2)[1]
        # 3. Remove the beginning '/'
        abs2 = abs2.strip('\\/') or abs2
        return os.path.abspath(os.path.join(abs1, abs2))

    @staticmethod
    def isContainedHostIdInfile(f_file, content):
        isContained = False
        with open(f_file, 'r') as d_file:
            for line in d_file.readlines():
                line_dict = json.loads(str(ast.literal_eval(line)).replace("'", "\""))
                if content == line_dict["host_id"]:
                    isContained = True
                    return isContained

        return isContained

    @staticmethod
    def addHostToFile(d_file, host):
        info_json = json.dumps(str(host), sort_keys=False, indent=4, separators=(',', ': '))
        os.umask(0o077)
        with open(d_file, 'a+') as host_file:
            host_file.write(info_json)
            host_file.write("\n")

    @staticmethod
    def getSubDirFiles(path):
        """
        desc: Subdirectory records and files need to be logged to the successConf
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
        desc: Query domain Whether host information is configured in the domain
        """
        isHostInDomain = False
        TARGETDIR = Format.get_git_dir()
        domainPath = os.path.join(TARGETDIR, domainName)
        hostPath = os.path.join(domainPath, "hostRecord.txt")
        if os.path.isfile(hostPath):
            isHostInDomain = True

        return isHostInDomain

    @staticmethod
    def isHostIdExist(hostPath, hostId):
        """
        desc: Query hostId exists within the current host domain management
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
    def get_file_content_by_readlines(d_file):
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
        if not os.path.exists(d_file):
            return ""
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
    def arch_sep(package_string):
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

    @staticmethod
    def get_git_dir():
        cf = configparser.ConfigParser()
        if os.path.exists(CONFIG):
            cf.read(CONFIG, encoding="utf-8")
        else:
            parent = os.path.dirname(os.path.realpath(__file__))
            conf_path = os.path.join(parent, "../../config/gala-ragdoll.conf")
            cf.read(conf_path, encoding="utf-8")
        git_dir = ast.literal_eval(cf.get("git", "git_dir"))
        return git_dir
