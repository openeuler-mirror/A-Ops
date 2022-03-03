import requests
import json

from ragdoll.models.domain import Domain
from ragdoll.models.domain_name import DomainName
from ragdoll.models.host import Host
from ragdoll.models.host_infos import HostInfos
from ragdoll.demo.conf import server_port
from ragdoll.encoder import JSONEncoder

class HostManage(object):
    def host_add(self, args):
        domain_name = args.domain_name
        host_id_list = args.host_id
        ip_list = args.ip
        ipv6_list = args.ipv6
        
        if len(host_id_list) != len(ip_list):
            print("ERROR: Input error!\n")
            return
        
        host_infos = []
        for i in range(len(host_id_list)):
            host_info = Host(host_id=host_id_list[i], ip=ip_list[i], ipv6=ipv6_list[i])
            host_infos.append(host_info)

        data = HostInfos(domain_name=domain_name, host_infos=host_infos)
        url = "http://0.0.0.0:{}/host/addHost".format(server_port)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data, cls=JSONEncoder), headers=headers)
        print(json.loads(response.text).get("msg"))
        return

    def host_query(self, args):
        domain_name = args.domain_name
        if not domain_name:
            print("ERROR: Input error!\n")
            return
        
        data = DomainName(domain_name=domain_name)
        url = "http://0.0.0.0:{}/host/getHost".format(server_port)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data, cls=JSONEncoder), headers=headers)

        if response.status_code != 200:
            print(json.loads(response.text).get("msg"))
        else:
            print("The following host are managed in domain_name:{}.".format(json.loads(response.text)))
        return

    def host_delete(self, args):
        domain_name = args.domain_name
        host_id_list = args.host_id
        ip_list = args.ip
        ipv6_list = args.ipv6
        
        if len(host_id_list) != len(ip_list):
            print("ERROR: Input error!\n")
            return
        
        host_infos = []
        for i in range(len(host_id_list)):
            host_info = Host(host_id=host_id_list[i], ip=ip_list[i], ipv6=ipv6_list[i])
            host_infos.append(host_info)
        
        data = HostInfos(domain_name=domain_name, host_infos=host_infos)
        url = "http://0.0.0.0:{}/host/deleteHost".format(server_port)
        headers = {"Content-Type": "application/json"}
        response = requests.delete(url, data=json.dumps(data, cls=JSONEncoder), headers=headers)
        print(json.loads(response.text).get("msg"))
        return