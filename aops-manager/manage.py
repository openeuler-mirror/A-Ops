#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: Manager that start aops-manager
"""
import argparse
from flask import Flask


def run_app(name):
    """
    Run manager server
    """
    module_name = 'aops_' + name
    app = Flask(module_name)

    module = __import__(module_name, fromlist=[module_name])
    for blue, api in module.BLUE_POINT:
        api.init_app(app)
        app.register_blueprint(blue)

    try:
        config = getattr(module.conf.configuration, name)
    except AttributeError:
        raise AttributeError("There is no config named %s" % name)

    ip = config.get('IP')
    port = config.get('PORT')
    app.run(host=ip, port=port)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--name', required=True)
    args = argparser.parse_args()
    run_app(args.name)
