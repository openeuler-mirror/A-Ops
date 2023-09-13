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
Author: jiaosimao
Description: kv tyep config analyze
"""
import re
from ragdoll.config_model.base_handler_config import BaseHandlerConfig


class KvConfig(BaseHandlerConfig):
    @staticmethod
    def parse_conf_to_dict(conf_info, space_type, yang_info):
        """
        将配置信息conf_info转为dict，但是并未校验配置项是否合法
        """
        conf_dict_list = list()

        conf_list = conf_info.strip().splitlines()
        for line in conf_list:
            if line is None or line.strip() == '' or line.strip()[0] in '#':
                continue
            re_domain = re.split("\s+", line)
            if space_type[str(yang_info)] == "":
                if len(re_domain) == 1:
                    return conf_dict_list
                re_list = re.split("\s", line.strip(), 1)
                conf_dict = dict()
                conf_dict[re_list[0]] = re_list[1]
                conf_dict_list.append(conf_dict)
            elif space_type[str(yang_info)] == "=":
                re_list = re.split("=", line.strip(), 1)
                conf_dict = dict()
                conf_dict[re_list[0]] = re_list[1]
                conf_dict_list.append(conf_dict)

        return conf_dict_list

    def read_conf(self, conf_info, space_type=None, yang_info=None):
        conf_dict_list = self.parse_conf_to_dict(conf_info, space_type, yang_info)
        if conf_dict_list:
            self.conf = conf_dict_list

    def write_conf(self, space_type=None, yang_info=None):
        content = ""
        conf_item = ""
        space_type = space_type[str(yang_info)]
        for conf_dict in self.conf:
            for key, value in conf_dict.items():
                if value is None:
                    continue
                if space_type == "":
                    conf_item = " ".join((key, value)).replace('\n', '\n\t')
                elif space_type == "=":
                    conf_item = "=".join((key, value)).replace('\n', '\n\t')
                content = content + conf_item + "\n"

        content = content + '\n'
        return content
