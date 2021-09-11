import requests
import json

data = {'infos': [{'host_id': '6777c1740fca11ec979a525400056d9d', 'config_list': ['/etc/coremail/coremail.conf']}]}
url = 'http://127.0.0.1:11111/manage/config/collect'


response = requests.request('post', url, json=data)
print(response.text)
print(type(response.text))

