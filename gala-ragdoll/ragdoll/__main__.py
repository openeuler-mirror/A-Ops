#!/usr/bin/env python3

import connexion
import configparser
import os
import ast
from io import StringIO

from ragdoll import encoder
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.prepare import Prepare

CONFIG = "/etc/ragdoll/gala-ragdoll.conf"

def main():
    # prepare to load config
    load_prepare()
    # load yang modules
    load_yang()
    # load port for ragdoll
    ragdoll_port = load_port()
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Configuration traceability'})
    app.run(port=ragdoll_port)


def load_prepare():
    git_dir, git_user_name, git_user_email = load_conf()
    prepare = Prepare(git_dir)
    prepare.mdkir_git_warehose(git_user_name, git_user_email)


def load_yang():
    yang_modules = YangModule()


def load_conf():
    cf = configparser.ConfigParser()
    if os.path.exists(CONFIG):
        cf.read(CONFIG, encoding="utf-8")
    else:
        cf.read("config/gala-ragdoll.conf", encoding="utf-8")
    git_dir = ast.literal_eval(cf.get("git", "git_dir"))
    git_user_name = ast.literal_eval(cf.get("git", "user_name"))
    git_user_email = ast.literal_eval(cf.get("git", "user_email"))
    return git_dir, git_user_name, git_user_email


def load_port():
    cf = configparser.ConfigParser()
    if os.path.exists(CONFIG):
        cf.read(CONFIG, encoding="utf-8")
    else:
        cf.read("config/gala-ragdoll.conf", encoding="utf-8")
    ragdoll_port = cf.get("ragdoll", "port")
    return ragdoll_port

if __name__ == '__main__':
    main()
