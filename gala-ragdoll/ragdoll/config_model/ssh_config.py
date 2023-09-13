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
Time: 2023-07-14 14:38:00
Author: jiaosimao
Description: sshd config analyze
"""
import json
import re

from ragdoll.utils.yang_module import YangModule
from ragdoll.const.conf_handler_const import NOT_SYNCHRONIZE, SYNCHRONIZED

SPACER_LIST = [' ', '\t']

class SshConfig(BaseHandlerConfig):

    def parse_conf_to_dict(self, conf_info):
        """
        将配置信息conf_info转为list，但是并未校验配置项是否合法
        """
        result_dict = {}
        error_conf = False

        raw_content_list = conf_info.split("\n")
        handle_content_list = list()
        for raw_line in raw_content_list:
            if raw_line.strip() == '' or raw_line.strip()[0] in '#':
                continue
            handle_content_list.append(raw_line)  # remove empty line & comment line

        if handle_content_list[0][0] in SPACER_LIST:
            error_conf = True
            return error_conf, result_dict

        index = 0
        current_session_key = ''
        for line in handle_content_list:
            if index < len(handle_content_list) - 1:
                next_element = handle_content_list[index + 1]
                # handle normal kv
                if line[0] not in SPACER_LIST and next_element[0] not in SPACER_LIST:
                    handle_result, key, str_value = self.parse_line_to_dict(line)
                    error_conf = handle_result
                    if handle_result is True:
                        break
                    result_dict[key] = str_value
                # handle session
                elif line[0] not in SPACER_LIST and next_element[0] in SPACER_LIST:
                    if line == current_session_key:
                        error_conf = True
                        break
                    current_session_key = line
                    result_dict[current_session_key] = list()
                # handle kv under session
                elif line[0] in SPACER_LIST:
                    handle_result, key, str_value = self.parse_line_to_dict(line)
                    error_conf = handle_result
                    if handle_result is True:
                        break
                    session_dict = dict()
                    session_dict[key] = str_value
                    result_dict[current_session_key].append(session_dict)
                index += 1
            else:
                # handle the last line & kv under session
                if line[0] in SPACER_LIST:
                    handle_result, key, str_value = self.parse_line_to_dict(line)
                    error_conf = handle_result
                    if handle_result is True:
                        break
                    session_dict = dict()
                    session_dict[key] = str_value
                    result_dict[current_session_key].append(session_dict)
                # handle the last line & normal kv
                else:
                    handle_result, key, str_value = self.parse_line_to_dict(line)
                    error_conf = handle_result
                    if handle_result is True:
                        break
                    result_dict[key] = str_value

        return error_conf, result_dict

    @staticmethod
    def parse_line_to_dict(line):
        handle_result = False
        line_list = re.split("\s+", line.strip())
        if len(line_list) == 1:
            handle_result = True
        key = line_list[0]
        value = line_list[1:]
        str_value = " ".join(value)
        return handle_result, key, str_value

    def load_yang_model(self, yang_info):
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(yang_info)  # get all xpath in yang_info

        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            section = real_path[2]
            option = real_path[3]

            if section not in self.yang:
                self.yang[section] = dict()
            self.yang[section][option] = None

    def read_conf(self, conf_info):
        error_conf, conf_dict_list = self.parse_conf_to_dict(conf_info)
        if error_conf is False:
            self.conf = conf_dict_list

    def write_conf(self):
        content = ""
        for key, value in self.conf.items():
            if value is not None and type(value) is str:
                conf_item = " ".join((key, str(value))).replace('\n', '\n\t')
                content = content + conf_item + "\n"
            elif value is not None and type(value) is list:
                content = content + key + "\n"
                for conf_info in value:
                    for conf_key, conf_value in conf_info.items():
                        conf_item = " ".join((conf_key, str(conf_value))).replace('\n', '\n\t')
                        content = content + "\t" + conf_item + "\n"
        return content

    @staticmethod
    def conf_compare(src_conf, dst_conf):
        """
        desc: 比较dst_conf和src_conf是否相同，dst_conf和src_conf均为序列化后的配置信息。
        return：dst_conf和src_conf相同返回SYNCHRONIZED
                dst_conf和src_conf不同返回NOT_SYNCHRONIZE
        """
        res = SYNCHRONIZED
        dst_conf_dict = json.loads(dst_conf)
        src_conf_dict = json.loads(src_conf)

        src_conf_keys = src_conf_dict.keys()
        dst_conf_keys = dst_conf_dict.keys()

        for src_key in src_conf_keys:
            if src_key not in dst_conf_keys:
                res = NOT_SYNCHRONIZE
                break
            src_content = src_conf_dict[src_key]
            dst_content = dst_conf_dict[src_key]
            if type(src_content) is str and src_content != dst_content:
                res = NOT_SYNCHRONIZE
                break
            elif type(src_content) is list:
                dst_str = str(dst_content)
                for src in src_content:
                    src_str = str(src)
                    if dst_str.find(src_str) == -1:
                        res = NOT_SYNCHRONIZE
                        break
                if res == NOT_SYNCHRONIZE:
                    break
        return res
