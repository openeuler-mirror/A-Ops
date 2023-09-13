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
Time: 2023-07-19 11:22:00
Author: jiaosimao
Description: limits config analyze
"""
import re
from ragdoll.config_model.base_handler_config import BaseHandlerConfig
from ragdoll.const.conf_handler_const import LIMITS_DOMAIN_RE, LIMITS_TYPE_VALUE, \
    LIMITS_ITEM_VALUE


class LimitsConfig(BaseHandlerConfig):

    @staticmethod
    def parse_conf_to_dict(conf_info):

        error_conf = False
        """
        将配置信息conf_info转为list，并校验配置项是否合法
        """
        conf_dict_list = list()

        conf_list = conf_info.strip().splitlines()
        for line in conf_list:
            if line is None or line.strip() == '' or line.strip()[0] in '#':
                continue
            strip_line = str(line.strip()).replace("\t", " ")
            line_list = str(strip_line.strip()).replace("\\s+", " ")
            res = list(filter(None, line_list.split(" ")))
            if len(res) != 4 or LIMITS_DOMAIN_RE.match(res[0]) is None \
                    or re.search(r'\b' + LIMITS_TYPE_VALUE + '\b', res[1]) is None \
                    or re.search(r'\b' + LIMITS_ITEM_VALUE + '\b', res[2]) is None:
                error_conf = True
            else:
                value_list = list()
                for value in res:
                    value_list.append(value)
                conf_dict_list.append(value_list)
        return error_conf, conf_dict_list

    def read_conf(self, conf_info):
        error_conf, conf_dict_list = self.parse_conf_to_dict(conf_info)
        if error_conf is False and conf_dict_list:
            self.conf = conf_dict_list

    def write_conf(self):
        content = ""
        for conf_list in self.conf:
            for value in conf_list:
                if value is not None:
                    content = content + value + "\t"
            content = content + '\n'
        content = content + '\n'
        return content
