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
from ragdoll.config_model.base_handler_config import BaseHandlerConfig
from ragdoll.const.conf_handler_const import FSTAB_COLUMN_NUM
from ragdoll.log.log import LOGGER

class FstabConfig(BaseHandlerConfig):
    """
    fstab 文件包含6列,用tab或空格分隔。对应字段为:
    <file system>	<dir>	<type>	<options>	<dump>	<pass>
    下面是一行fstab配置的例子：
    /dev/sda1              /             ext4      defaults      0      1
    """

    @staticmethod
    def parse_conf_to_dict(conf_info):

        error_conf = False
        res = list()
        conf_info_list = conf_info.split("\n")
        for line in conf_info_list:
            if line.strip() == '' or line.strip()[0] in '#':
                continue
            line_list = re.split("\s+", line)
            if len(line_list) != FSTAB_COLUMN_NUM:
                error_conf = True
                break
            res.append(line_list)

        return error_conf, res

    def read_conf(self, conf_info):
        error_conf, res_list = self.parse_conf_to_dict(conf_info)
        if error_conf is False and res_list:
            self.conf = res_list

    def write_conf(self):
        content = ""
        for value_list in self.conf:
            line = " ".join(str(value) for value in value_list)
            content = content + line + "\n"
        return content
