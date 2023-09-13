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
Time: 2023-07-19 11:20:00
Author: GengLei
Description: /etc/hosts config handler
"""
import re
import json

from ragdoll.log.log import LOGGER
from ragdoll.utils.yang_module import YangModule
from ragdoll.const.conf_handler_const import NOT_SYNCHRONIZE, SYNCHRONIZED

ipv4 = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

ipv6 = re.compile('^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){1,7}:)|'
                  '(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){5}(:[0-9A-Fa-f]{1,4}){1,2})|'
                  '(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4}){1,3})|'
                  '(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){1,5})|'
                  '([0-9A-Fa-f]{1,4}:(:[0-9A-Fa-f]{1,4}){1,6})|'
                  '(:(:[0-9A-Fa-f]{1,4}){1,7})|'
                  '(([0-9A-Fa-f]{1,4}:){6}(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){5}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4})'
                  '{0,1}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){0,2}:(\\d|[1-9]\\d|1\\d{2}|'
                  '2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){0,3}:(\\d|[1-9]\\d|1\\d{2}|'
                  '2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '([0-9A-Fa-f]{1,4}:(:[0-9A-Fa-f]{1,4}){0,4}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(:(:[0-9A-Fa-f]{1,4}){0,5}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}))$')


class HostsConfig(BaseHandlerConfig):

    @staticmethod
    def _parse_network_conf_to_dict(conf_info):

        res = dict()
        error_conf = False

        conf_info_list = conf_info.split("\n")
        for line in conf_info_list:
            if line.strip() == '' or line.strip()[0] in '#':
                continue
            ip_domain = re.split("\s+", line)
            if len(ip_domain) == 1:
                error_conf = True
                LOGGER.info("ip_domain contains incorrect formatting")
                break
            ip = ip_domain[0]
            if ipv4.match(ip) or ipv6.match(ip):
                list_value = ip_domain[1:]
                str_value = " ".join(list_value)
                res[ip] = str_value
            else:
                error_conf = True
                LOGGER.info("ip does not meet the ipv4 or ipv6 format")
                break

        return error_conf, res

    def read_conf(self, conf_info):
        error_conf, dict_res = self._parse_network_conf_to_dict(conf_info.strip())
        if not error_conf:
            self.conf = dict_res

    @staticmethod
    def conf_compare(dst_conf, src_conf):
        res = SYNCHRONIZED
        dst_conf_dict = json.loads(dst_conf)
        src_conf_dict = json.loads(src_conf)

        dst_conf_keys = dst_conf_dict.keys()
        src_conf_keys = src_conf_dict.keys()

        for src_key in src_conf_keys:
            if src_key not in dst_conf_keys:
                res = NOT_SYNCHRONIZE
                break
            if str(dst_conf_dict[src_key]) != str(src_conf_dict[src_key]):
                res = NOT_SYNCHRONIZE
                break
        return res

    def write_conf(self):
        content = ""
        for key, value in self.conf:
            if value is not None:
                conf_item = " ".join((key, str(value))).replace('\n', '\n\t')
                content = content + conf_item + "\n"
        return content
