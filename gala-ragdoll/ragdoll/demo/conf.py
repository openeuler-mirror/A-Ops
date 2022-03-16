
import configparser
import os


CONFIG = "/etc/ragdoll/gala-ragdoll.conf"


cf = configparser.ConfigParser()
if os.path.exists(CONFIG):
    cf.read(CONFIG, encoding="utf-8")
else:
    cf.read("../../config/gala-ragdoll.conf", encoding="utf-8")

server_port = cf.get("ragdoll", "port")

