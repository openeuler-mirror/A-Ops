#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: register method for all commands
Class: A-Ops Commands
"""

# 'import xxxxCommand' would be used in the args_parser() to register command
from aops_cli.base_cmd import BaseCommand
from aops_cli.commons.exc import Error
from aops_cli.commands.host_cmd import HostCommand  # pylint: disable=unused-import
from aops_cli.commands.group_cmd import GroupCommand  # pylint: disable=unused-import
from aops_cli.commands.template_cmd import TemplateCommand  # pylint: disable=unused-import
from aops_cli.commands.task_cmd import TaskCommand  # pylint: disable=unused-import
from aops_cli.commands.account_cmd import AccountCommand  # pylint: disable=unused-import
from aops_cli.commands.certificate_cmd import CertificateCommand  # pylint: disable=unused-import
from aops_cli.commands.stat_cmd import StatCommand  # pylint: disable=unused-import


def main():
    """
    Description: entrance for all command line

    Raises:
        Error: An error occurred while executing the command
    """
    try:
        for sub_cls in BaseCommand.__subclasses__():
            # get the all subclass of BaseCommand and register the subcommand one by one
            BaseCommand.register_command(sub_cls())
            # add all arguments' attribution into instance
        sub_cls.args_parser() # pylint: disable=W0631
    except Error:
        print('Command execution error please try again')


if __name__ == '__main__':
    main()
