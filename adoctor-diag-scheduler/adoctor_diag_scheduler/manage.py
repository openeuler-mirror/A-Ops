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
Description: Manager that start adoctor_diag_scheduler
"""
#!/usr/bin/python3

from flask import Flask
from adoctor_diag_scheduler import blue_point
from adoctor_diag_scheduler.conf import diag_configuration


def flask_app():
    """
    Diag service manager.
    """
    app = Flask(__name__)

    for blue, api in blue_point:
        api.init_app(app)
        app.register_blueprint(blue)

    return app


app = flask_app()

if __name__ == "__main__":
    app = flask_app()
    diag_ip = diag_configuration.diag_scheduler.get('IP')
    diag_port = diag_configuration.diag_scheduler.get('PORT')
    app.run(port=diag_port, host=diag_ip)
