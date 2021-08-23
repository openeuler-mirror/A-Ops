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
"""
Time:
Author:
Description:
"""
from marshmallow import ValidationError


def validate(verifier, data, load=False):
    """
    Validation method

    Args:
        verifier(class): the class of the validator
        data(dict): parameter to be verified
        load(bool): do parameter deserializing if load is set to true

    Returns:
        dict: verified parameter
        dict: messages when verified failed
    """
    result = data
    errors = dict()
    if load:
        try:
            result = verifier().load(data)
        except ValidationError as err:
            errors = err.messages
    else:
        errors = verifier().validate(data)

    return result, errors
