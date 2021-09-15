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
Description: Base method for custom commands
Class: BaseCommand
"""
import argparse
from collections import namedtuple
from abc import abstractmethod


class BaseCommand:
    """
    Description: Basic attributes used for command invocation
    Attributes:
        params(argparse.Namespace): Command line parameters
        sub_parse: Subcommand parameters
        sub_args: namedtuple for generating subcommand parameters
    """

    parser = argparse.ArgumentParser(
        description="A-Ops is a project to mantain servers automatically.",
        prog='A-Ops')

    subparsers = parser.add_subparsers(title='command',
                                       help='A-Ops is a project to maintain servers automatically.',
                                       required=True,
                                       dest='sub_parse_name',
                                       metavar='start')

    def __init__(self):
        """
        Description: Instance initialization
        """
        self.params = []
        self.sub_parse = None
        self.sub_args = namedtuple(
            'sub_args',
            ['sub_command', 'help', 'default', 'action', 'nargs', 'required', 'choices']
        )

    def add_subcommand(self, sub_command, help_desc):
        """
        Description: add subcommand with releaseIssueID and gitee ID as sub_parse argument
        Args:
            sub_command(str): sub command of the cli
            help_desc(str): help description of the sub command

        """
        self.sub_parse = BaseCommand.subparsers.add_parser(
            sub_command, help=help_desc)

    @staticmethod
    def register_command(command):
        """
        Description: Registration of commands

        Args:
            command: commands for aops

        """
        command.sub_parse.set_defaults(func=command.do_command)

    @classmethod
    def args_parser(cls):
        """
        Description: argument parser

        """
        args = cls.parser.parse_args()
        args.func(args)

    @abstractmethod
    def do_command(self, params):
        """
        Description: Method which wound need to be implemented by subcommands

        Args:
            params: Command line parameters
        Returns:

        """
