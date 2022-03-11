import requests
import json

from ragdoll.models.domain import Domain
from ragdoll.demo.conf import server_port
from ragdoll.encoder import JSONEncoder


class DomainManage(object):
    def domain_create(self, args):
        domain_name_list = args.domain_name
        priority_list = args.priority
        if len(domain_name_list) != len(priority_list):
            print("ERROR: Input error!\n")
            return

        data = []
        for i in range(min(len(domain_name_list), len(priority_list))):
            domain = {"domain_name":str(domain_name_list[i]), "priority": int(priority_list[i])}
            domain = Domain(domain_name=str(domain_name_list[i]), priority=int(priority_list[i]))
            data.append(domain)
        url = "http://0.0.0.0:{}/domain/createDomain".format(server_port)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data, cls=JSONEncoder), headers=headers)
        
        print(json.loads(response.text).get("msg"))
        return
    
    def domain_delete(self, args):
        domain_name_list = args.domain_name
        headers = {"Content-Type": "application/json"}
        for domain_name in domain_name_list:
            url = "http://0.0.0.0:{}/domain/deleteDomain?domainName={}".format(server_port, domain_name)
            response = requests.delete(url, headers=headers)
            print(json.loads(response.text).get("msg"))
        return
    
    def domain_query(self, args):
        if not args:
            return
        url="http://0.0.0.0:{}/domain/queryDomain".format(server_port)
        response = requests.post(url)
        
        if response.status_code == 200:
            _domain_info = []
            if len(json.loads(response.text)) > 0:
                for i in json.loads(response.text):
                    _domain_info.append(i.get("domainName"))
            domain_info = "The following configuration domains are managed:{}.".format(_domain_info)
            print(domain_info)
        else:
            print(json.loads(response.text).get("msg"))
        return
