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
url set of diagnostic module
"""
from . import view
from aops_utils.conf.constant import DIAG_EXECUTE_DIAG, DIAG_GET_PROGRESS, DIAG_IMPORT_TREE,\
    DIAG_GET_TREE, DIAG_DELETE_TREE, DIAG_GET_TASK, DIAG_GET_REPORT, DIAG_GET_REPORT_LIST, \
    DIAG_DELETE_REPORT


urls = [
    (view.AddDiagTree, DIAG_IMPORT_TREE, ["POST"]),
    (view.DelDiagTree, DIAG_DELETE_TREE, ["DELETE"]),
    (view.GetDiagTree, DIAG_GET_TREE, ["POST"]),
    (view.ExecuteDiag, DIAG_EXECUTE_DIAG, ["POST"]),
    (view.GetDiagTask, DIAG_GET_TASK, ["POST"]),
    (view.Progress, DIAG_GET_PROGRESS, ["POST"]),
    (view.GetDiagReport, DIAG_GET_REPORT, ["POST"]),
    (view.GetDiagReportList, DIAG_GET_REPORT_LIST, ["POST"]),
    (view.DelDiagReport, DIAG_DELETE_REPORT, ["DELETE"])
]
