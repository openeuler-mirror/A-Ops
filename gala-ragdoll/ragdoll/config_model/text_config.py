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
Time: 2023-07-19 11:23:00
Author: liulei
Description: text type config analyze
"""
import json

from ragdoll.utils.yang_module import YangModule
from ragdoll.const.conf_handler_const import NOT_SYNCHRONIZE
from ragdoll.const.conf_handler_const import SYNCHRONIZED


class TextConfig:
    def __init__(self):
        self.conf = list()
        self.yang = list()

    @staticmethod
    def parse_conf_to_dict(conf_info):
        """
        将配置信息conf_info转为list，但是并未校验配置项是否合法
        """
        conf_dict_list = list()

        conf_list = conf_info.strip().splitlines()
        for line in conf_list:
            if line is None or line.strip() == '' or line.strip()[0] in '#;':
                continue

            strip_line = str(line.strip()).replace("\t", " ")
            conf_dict_list.append(strip_line)
        return conf_dict_list

    def load_yang_model(self, yang_info):
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(yang_info)  # get all xpath in yang_info
        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            option = real_path[2]

            if option not in self.yang:
                self.yang.append(option)

    def read_conf(self, conf_info):
        conf_dict_list = self.parse_conf_to_dict(conf_info)
        if conf_dict_list:
            self.conf = conf_dict_list

    def write_conf(self):
        content = ""
        for value in self.conf:
            if value is not None:
                content = content + value + "\n"
        content = content + '\n'
        return content

    def read_json(self, conf_json):
        """
        desc: 将json格式的配置文件内容结构化成Class conf成员。
        """
        conf_list = json.loads(conf_json)
        self.conf = conf_list

    @staticmethod
    def conf_compare(dst_conf, src_conf):
        """
        desc: 比较dst_conf和src_conf是否相同，dst_conf和src_conf均为序列化后的配置信息。
        return：dst_conf和src_conf相同返回SYNCHRONIZED
                dst_conf和src_conf不同返回NOT_SYNCHRONIZE
        """
        res = SYNCHRONIZED
        dst_conf_dict = json.loads(dst_conf)
        src_conf_dict = json.loads(src_conf)

        for dst_conf in dst_conf_dict:
            str_dst_conf = str(dst_conf)
            if str(src_conf_dict).find(str_dst_conf) == -1:
                res = NOT_SYNCHRONIZE
                break
        return res
