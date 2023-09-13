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

import re
import json
import copy
from collections import OrderedDict as _default_dict

from ragdoll.utils.yang_module import YangModule
from ragdoll.config_model.base_config import BaseConfig


# regular expressions for parsing section headers
SECTCRE = re.compile(
    r'\['                                 # [
    r'(?P<header>[^]]+)'                  # very permissive!
    r'\]'                                 # ]
    )

# regular expressions for parsing section options
OPTCRE = re.compile(
    r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
    r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                          # followed by separator
                                          # (either : or =), followed
                                          # by any # space/tab
    r'(?P<value>.*)$'                     # everything up to eol
    )


class IniConfig(BaseConfig):
    def _parse_conf_to_dict(self, conf_info):
        """
        将配置信息conf_info转为dict，但是并未校验配置项是否合法
        """
        conf_dict = _default_dict()

        conf_list = conf_info.strip().splitlines()
        cur_sect = _default_dict()
        for line in conf_list:
            line = line.strip()
            if line.strip() == '' or line[0] in '#;':
                continue

            matched_section = SECTCRE.match(line)
            if matched_section:
                sect_name = matched_section.group('header')
                if sect_name in conf_dict:
                    cur_sect = conf_dict[sect_name]
                else:
                    cur_sect = _default_dict()
                    cur_sect['__name__'] = sect_name
                    conf_dict[sect_name] = cur_sect
            else:
                matched_option = OPTCRE.match(line)
                if matched_option:
                    opt_name, vi, opt_val = matched_option.group('option', 'vi', 'value')
                    cur_sect[opt_name.strip()] = opt_val
                else:
                    return False
        return conf_dict


    def _get_options(self, conf, section_name):
        options = _default_dict()
        options = options if section_name not in conf else copy.deepcopy(conf[section_name]) 
        return options


    def _check_option(self, yang, option_list):
        """
        检查option_list是否在yang的某个section中（模糊匹配）。

        yang: 目标yang
        option_list: 待查询options
        """
        res = ""
        if not yang or not option_list:
            return res

        for section in yang.keys():
            options = list(self._get_options(yang, section))
            if not options:
                continue

            count = 0
            for _option in list(option_list):
                if _option in options:
                    count = count + 1

            if count == 1 and len(option_list) == 1:
                res = section
                break
            else:
                if count > 2:
                    res = section
                    break
        return res



    def load_yang_model(self, yang_info):
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(yang_info)   # get all xpath in yang_info

        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            section = real_path[2]
            option = real_path[3]

            if section not in self.yang:
                self.yang[section] = _default_dict()
            self.yang[section][option] = None


    def read_conf(self, conf_info):
        conf_dict = self._parse_conf_to_dict(conf_info)
        if not conf_dict:
            return False
        section_list = conf_dict.keys()

        res = _default_dict()
        for section in section_list:
            option_list = self._get_options(conf_dict, section)
            if not option_list:
                continue

            matched_section = self._check_option(self.yang, option_list)
            if matched_section:
                for option in option_list:
                    if option == "__name__":
                        continue
                    value = conf_dict.get(section, {}).get(option)
                    if section not in res.keys():
                        res[section] = _default_dict()
                    res[section][option] = value
        self.conf = res


    def write_conf(self):
        content = ""

        for section in self.conf:
            content = content + "[{}]\n".format(section)
            for (key, value) in self.conf[section].items():
                if key == "__name__":
                    continue
                if value is not None:
                    conf_item = " = ".join((key, str(value).replace('\n', '\n\t')))
                content = content + conf_item + '\n'
            content = content + '\n'
        return content

