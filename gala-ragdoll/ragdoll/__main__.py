#!/usr/bin/env python3

import connexion
from io import StringIO

from ragdoll import encoder
from ragdoll.utils.yang_module import YangModule
from ragdoll.utils.prepare import Prepare

def main():
    # 服务启动时的预准备动作
    prepare = Prepare()
    prepare.mdkir_git_warehose()
    # load_yang()
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Configuration traceability'})
    app.run(port=8080)

def load_yang():
    yang_modules = YangModule()
    modulesList = yang_modules.loadYangModules()

if __name__ == '__main__':
    main()