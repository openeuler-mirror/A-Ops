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
import sys
import argparse
from collections import namedtuple
from abc import abstractmethod
import datetime as dt
from datetime import datetime

from aops_utils import time_utils
from aops_utils.validate import validate_time
from aops_utils.log.log import LOGGER
from aops_utils.restful.response import MyResponse

TIME_FORMAT = "%Y%m%d-%H:%M:%S"


def time_check_generate(starttime, endtime):
    """
    Description: check and generate time

    Args:
        starttime: starttime of the command
        endtime: endtime of the command
    Returns:
        [starttime, endtime]: list of starttime and endtime
    Raises:

    """

    if starttime == "":
        if endtime == "":
            endtime = datetime.now()
            starttime = endtime + dt.timedelta(hours=-1)
        else:
            if not validate_time(endtime, TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s',
                             TIME_FORMAT)
                sys.exit(0)
            starttime = datetime.strptime(endtime, TIME_FORMAT) + dt.timedelta(hours=-1)
    else:
        if endtime == "":
            if not validate_time(starttime, TIME_FORMAT):
                LOGGER.error('The start time format is not correct, please refer to %s',
                             TIME_FORMAT)
                sys.exit(0)
            endtime = datetime.strptime(starttime, TIME_FORMAT) + dt.timedelta(hours=+1)

    starttime = starttime if isinstance(starttime, str) else starttime.strftime(TIME_FORMAT)
    endtime = endtime if isinstance(endtime, str) else endtime.strftime(TIME_FORMAT)
    starttime, endtime = time_utils.time_transfer(starttime, endtime)

    print("check part start", starttime, endtime)
    return [starttime, endtime]


def str_split(string):
    """
    Description: split str args into list
    Args:
        string(str): The string need to be splited.
    Returns:
        list of items

    """
    if string is not None and len(string) != 0:
        return string.split(",")
    return []


def cli_request(action, manager_url, pyload, header, access_token):
    """
    cli request to manager
    Args:
        action(str): actions of requests
        manager_url(str): route
        pyload(dict): request body
        header(dict): request header
        access_token(str): access token of users

    Returns:
        json: response of manager
    """
    header['access_token'] = access_token
    result = MyResponse.get_response(action, manager_url, pyload, header)
    print(result)
    return result


def add_query_args(sub_parse, item_list):
    """
    Add query args of the sub parse.
    Args:
        item_list(list): list for sort items
        sub_parse(sub_parse): sub_parse of the command
    Returns:

    """
    sub_parse.add_argument(
        '--sort',
        help='sort for the query result, null is no sort',
        nargs='?',
        type=str,
        default="",
        choices=item_list
    )

    sub_parse.add_argument(
        '--direction',
        help='asc or desc of the sort',
        nargs='?',
        type=str,
        default="asc",
        choices=['asc', 'desc']
    )


def add_access_token(sub_parse):
    """
    Add access_token of the sub parse.
    Args:
        sub_parse(sub_parse): sub_parse of the command

    Returns:

    """
    sub_parse.add_argument(
            '--access_token',
            help='The access token for operations',
            nargs='?',
            type=str,
            required=True
    )


class BaseCommand:
    """
    Description: Basic attributes used for command invocation
    Attributes:
        params(argparse.Namespace): Command line parameters
            e.g.
                Namespace(action='add',
                        func=<bound method HostCommand.
                            do_command of <modules.cli.
                            commands.hostCmd.
                            HostCommand object at 0x1096c6d10>>,
                        host_group_name='',
                        host_list='',
                        host_name='me',
                        management=False,
                        password='xx',
                        public_ip='11.11.11.11',
                        ssh_port=22,
                        subparser_name='host',
                        user_name='xxx',
                        verbose=False)
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
