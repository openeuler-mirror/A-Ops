#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
from typing import Dict, Tuple
from flask import jsonify

from aops_utils.restful.response import BaseResponse
from aops_utils.restful.status import SUCCEED

from aops_check.core.experiment.algorithm.scene_identify.package_weight import PackageWeightIdentify
from aops_check.utils.schema.scene import IdentifySceneSchema


class RecognizeScene(BaseResponse):
    @staticmethod
    def _handle(args: Dict) -> Tuple[int, Dict]:
        """
        generate uuid
        """
        result = {}
        applications = args["applications"]
        identify_algo = PackageWeightIdentify(applications)
        scene, collect_items = identify_algo.get_scene()
        result["scene_name"] = scene
        result["collect_items"] = collect_items
        return SUCCEED, result

    def post(self):
        """
        call scene identification algorithm to identify a host's scene
        """
        return jsonify(self.handle_request(IdentifySceneSchema, self))
