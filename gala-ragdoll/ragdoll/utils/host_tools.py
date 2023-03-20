import os
import configparser
import ast

CONFIG = "/etc/ragdoll/gala-ragdoll.conf"

class HostTools(object):
    def __init__(self):
        self._target_dir = self.load_git_dir()
        self._host_file = "hostRecord.txt"

    @property
    def target_dir(self):
        return self._target_dir

    @target_dir.setter
    def target_dir(self, target_dir):
        self._target_dir = target_dir

    @property
    def host_file(self):
        return self._host_file

    @host_file.setter
    def host_file(self, host_file):
        self._host_file = host_file

    def isHostIdExist(self, hostPath, hostId):
        """
        desc: 查询hostId是否存在当前的host域管理范围内
        """
        isHostIdExist = False
        if os.path.isfile(hostPath) and os.stat(hostPath).st_size > 0:
            with open(hostPath) as h_file:
                for line in h_file.readlines():
                    if str(hostId) in line:
                        isHostIdExist = True
                        break

        return isHostIdExist

    def getHostExistStatus(self, domain, hostList):
        """
        desc: return two list about the status of the host exists
        example:
            input hostList: [{'host_id': '551d02da-7d8c-4357-b88d-15dc55ee22cc',
                              'ip': '210.22.22.150',
                              'ipv6': 'None'}]
            output existHost:['551d02da-7d8c-4357-b88d-15dc55ee22cc']
        """
        if len(hostList) == 0:
            return None, None
        domainPath = os.path.join(self._target_dir, domain)
        hostPath = os.path.join(domainPath, self._host_file)
        existHost = []
        failedHost = []
        for d_host in hostList:
            d_hostId = d_host.get('hostId')
            isHostIdExist = self.isHostIdExist(hostPath, d_hostId)
            if isHostIdExist:
                existHost.append(d_hostId)
            else:
                failedHost.append(d_hostId)
        return existHost, failedHost

    def getHostList(self, domainHost) -> []:
        """
        desc：return a host list from the result of the /host/getHost
        example:
            domainHost is : [{'hostId': '551d02da-7d8c-4357-b88d-15dc55ee22cc', 'ip': '210.22.22.150', 'ipv6': 'None'}]
            hostList is: [{
                                "hostId" : '551d02da-7d8c-4357-b88d-15dc55ee22cc'
                            }]
        """
        res = []
        for d_host in domainHost:
            hostId = int(d_host.get('hostId'))
            print("the host Id is : {}".format(hostId))
            d_host = {}
            d_host["hostId"] = hostId
            res.append(d_host)

        return res

    def load_git_dir(self):
        cf = configparser.ConfigParser()
        if os.path.exists(CONFIG):
            cf.read(CONFIG, encoding="utf-8")
        else:
            parent = os.path.dirname(os.path.realpath(__file__))
            conf_path = os.path.join(parent, "../../config/gala-ragdoll.conf")
            cf.read(conf_path, encoding="utf-8")
        git_dir = ast.literal_eval(cf.get("git", "git_dir"))
        return git_dir
