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
Description: Template  method's entrance for custom commands
Class:TemplateCommand
"""
import sys

from aops_cli.base_cmd import BaseCommand
from aops_utils.validate import name_check, str_split
from aops_utils.conf.constant import IMPORT_TEMPLATE, DELETE_TEMPLATE, GET_TEMPLATE
from aops_utils.readconfig import read_yaml_config_file
from aops_utils.restful.helper import make_manager_url
from aops_utils.cli_utils import add_page, cli_request, add_access_token, add_query_args


class TemplateCommand(BaseCommand):
    """
    Description: template' operations
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='template',
                            help_desc="templates' operations")
        self.sub_parse.add_argument(
            '--action',
            help='template actions: import, delete, query',
            nargs='?',
            type=str,
            required=True,
            choices=['import', 'delete', 'query'])

        self.sub_parse.add_argument(
            '--template_name',
            help='template name',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--template_list',
            help='list of template names',
            nargs='?',
            type=str,
            default="")

        self.sub_parse.add_argument(
            '--template_content',
            help='template content read from the template file',
            nargs='?',
            type=str)

        self.sub_parse.add_argument(
            '--description',
            help='description  of templates',
            nargs='?',
            type=str,
            default="The template's description is null")

        add_access_token(self.sub_parse)
        add_query_args(self.sub_parse, ['template_name'])
        add_page(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters

        """

        action = params.action

        action_dict = {
            'import': self.manage_requests_import_template,
            'delete': self.manage_requests_delete_template,
            'query': self.manage_requests_query_template
        }

        action_dict.get(action)(params)

    @staticmethod
    def manage_requests_import_template(params):
        """
        Description: Executing add command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
        yaml_path = params.template_content
        yaml_content = read_yaml_config_file(yaml_path)
        template_name = str_split(params.template_name)
        if len(template_name) != 1:
            print("Only one template can be accepted, and ',' cannot be contained in name.")
            sys.exit(0)
        if not yaml_content:
            print("Invalid file: only yaml file can be accepted.")
            print("Please retry with a valid file.")
            sys.exit(0)
        manager_url, header = make_manager_url(IMPORT_TEMPLATE)
        pyload = {
            "template_name": template_name[0],
            "template_content": yaml_content,
            "description": params.description,
        }

        return cli_request('POST', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_delete_template(params):
        """
        Description: Executing delete request
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """

        templates = str_split(params.template_list)
        manager_url, header = make_manager_url(DELETE_TEMPLATE)

        if len(templates) == 0:
            print("No template will be deleted, because of the empty template list.")
            print("Please check your template list if you want to delete templates.")
            sys.exit(0)
        name_check(templates)
        pyload = {
            "template_list": templates
        }

        return cli_request('DELETE', manager_url, pyload, header, params.access_token)

    @staticmethod
    def manage_requests_query_template(params):
        """
        Description: Executing query request
        Args:
            params: Command line parameters
        Returns:
            dict: body of response
        """

        templates = str_split(params.template_list)
        if len(templates) != 0:
            name_check(templates)
        manager_url, header = make_manager_url(GET_TEMPLATE)
        pyload = {
            "page": params.page,
            "per_page": params.per_page,
            "template_list": templates
        }
        if params.sort is not None:
            pyload["sort"] = params.sort
            pyload["direction"] = params.direction

        return cli_request('POST', manager_url, pyload, header, params.access_token)
