#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/8/23 20:20
docs: __init__.py
description: Add view and url into api
"""
from flask.blueprints import Blueprint
from flask_restful import Api
from adoctor_check_scheduler.url import urls


adoctor_check_scheduler = Blueprint('check', __name__)

api = Api()

for view, url, operation in urls:
    api.add_resource(view, url)

blue_point = [
    (adoctor_check_scheduler, api)
]
