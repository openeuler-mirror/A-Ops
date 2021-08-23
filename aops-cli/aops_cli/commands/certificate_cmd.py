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
Description: certificate method's entrance for custom commands
Class:CertificateCommand
"""

from aops_cli.base_cmd import BaseCommand, cli_request, add_access_token
from aops_utils.restful.helper import make_manager_url
from aops_utils.conf.constant import USER_CERTIFICATE


class CertificateCommand(BaseCommand):
    """
    Description: accounts' operations
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super().__init__()
        self.add_subcommand(sub_command='certificate',
                            help_desc="certification's operations")

        self.sub_parse.add_argument(
            '--key',
            help='The key to crypt.',
            nargs='?',
            type=str,
            required=True
        )

        add_access_token(self.sub_parse)

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params(argparse.Namespace): Command line parameters
        """
        return self.manage_requests_certification(params)

    @staticmethod
    def manage_requests_certification(params):
        """
        Description: Executing certification request
        Args:
            params: Command line parameters
        Returns:
            dict: response of the backend
        """
        manager_url, header = make_manager_url(USER_CERTIFICATE)

        pyload = {
            "key": params.key
        }

        return cli_request('POST', manager_url, pyload, header, params.access_token)
