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
@FileName: resolv_config.py
@Time: 2023/7/31 15:31
@Author: JiaoSiMao
Description:
"""
import re
from ragdoll.config_model.base_handler_config import BaseHandlerConfig
from ragdoll.const.conf_handler_const import RESOLV_KEY_VALUE


class ResolvConfig(BaseHandlerConfig):

    @staticmethod
    def parse_conf_to_dict(conf_info):
        """
        将配置信息conf_info转为list，并校验配置项是否合法
        """
        conf_dict_list = list()
        error_conf = False

        conf_list = conf_info.strip().splitlines()
        for line in conf_list:
            if line is None or line.strip() == '' or line.strip()[0] in '#':
                continue
            re_list = re.split("\\s+", line.strip(), 1)
            if len(re_list) == 1 or re.search(r'\b' + RESOLV_KEY_VALUE + '\b', re_list[0]) is None:
                error_conf = True
            else:
                conf_dict = dict()
                conf_dict[re_list[0]] = re_list[1]
                conf_dict_list.append(conf_dict)
        return error_conf, conf_dict_list

    def read_conf(self, conf_info):
        error_conf, conf_dict_list = self.parse_conf_to_dict(conf_info)
        if error_conf is False and conf_dict_list:
            self.conf = conf_dict_list

    def write_conf(self):
        content = ""
        for conf_dict in self.conf:
            for key, value in conf_dict.items():
                if value is not None:
                    conf_item = " ".join((key, value)).replace('\n', '\n\t')
                    content = content + conf_item + "\n"
        content = content + '\n'
        return content
