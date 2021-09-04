#!/usr/bin/python3
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

def add_page(sub_parse):
    """
    Add access_token of the sub parse.
    Args:
        sub_parse(sub_parse): sub_parse of the command
    """
    sub_parse.add_argument(
        '--page',
        help='page of the query',
        nargs='?',
        type=int,
        default=1
    )

    sub_parse.add_argument(
        '--per_page',
        help='items per page.',
        nargs='?',
        type=int,
        default=20
    )
