#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
@FileName: base_handler_config.py
@Time: 2023/9/5 17:17
@Author: JiaoSiMao
Description:
"""
import json

from ragdoll.const.conf_handler_const import SYNCHRONIZED, NOT_SYNCHRONIZE
from ragdoll.utils.yang_module import YangModule


class BaseHandlerConfig(object):
    def __init__(self):
        self.conf = list()
        self.yang = list()

    def read_conf(self, conf_info):
        """
        desc: 将配置信息conf_info结构化成class BaseHandlerConfig内conf成员。

        conf_info: 配置信息，str类型
        """
        pass

    def write_conf(self):
        """
        desc: 将class BaseHandlerConfig实例成员conf反结构化成配置文件文本内容。
        return: str
        """
        pass

    def read_json(self, conf_json):
        """
        desc: 将json格式的配置文件内容结构化成Class BaseHandlerConfig内conf成员。
        """
        conf_list = json.loads(conf_json)
        self.conf = conf_list

    def load_yang_model(self, yang_info):
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(yang_info)  # get all xpath in yang_info

        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            option = real_path[2]

            if option not in self.yang:
                self.yang.append(option)

    def conf_compare(self, src_conf, dst_conf):
        """
        desc: 比较dst_conf和src_conf是否相同，dst_conf和src_conf均为序列化后的配置信息。
        return：dst_conf和src_conf相同返回SYNCHRONIZED
                dst_conf和src_conf不同返回NOT_SYNCHRONIZE
        """
        res = SYNCHRONIZED
        dst_conf_dict = json.loads(dst_conf)
        src_conf_dict = json.loads(src_conf)

        for src_conf in src_conf_dict:
            str_src_conf = str(src_conf)
            if str(dst_conf_dict).find(str_src_conf) == -1:
                res = NOT_SYNCHRONIZE
                break
        return res
