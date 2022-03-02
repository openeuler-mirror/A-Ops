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
Description: manager constant
"""
import os
from aops_utils.conf.constant import BASE_CONFIG_PATH

# path of cve-manager configuration
CVE_MANAGER_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'cve-manager.ini')

# template repo for downloading
TEMPLATE_REPO_STR = "[update]\n" \
                    "name=update\n" \
                    "baseurl=http://repo.openeuler.org/openEuler-21.03/update/$basearch/\n" \
                    "enabled=0\n" \
                    "gpgcheck=1\n" \
                    "gpgkey=http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-" \
                    "GPG-KEY-openEuler"


class ANSIBLE_TASK_STATUS:
    SUCCEED = "succeed"
    UNREACHABLE = "unreachable"
    FAIL = "fail"


class CVE_HOST_STATUS:
    FIXED = "fixed"
    UNFIXED = "unfixed"
    RUNNING = "running"
    UNKNOWN = "unknown"


class REPO_STATUS:
    SUCCEED = "set"
    FAIL = "unset"
    RUNNING = "running"
    UNKNOWN = "unknown"


class CVE_SCAN_STATUS:
    SCANNING = "scanning"
    DONE = "done"


# route of repo related interface
VUL_REPO_IMPORT = "/vulnerability/repo/import"
VUL_REPO_GET = "/vulnerability/repo/get"
VUL_REPO_UPDATE = "/vulnerability/repo/update"
VUL_REPO_DELETE = "/vulnerability/repo/delete"
VUL_REPO_TEMPLATE_GET = "/vulnerability/repo/template/get"

# route of cve related interface
VUL_CVE_OVERVIEW = "/vulnerability/cve/overview"
VUL_CVE_LIST_GET = "/vulnerability/cve/list/get"
VUL_CVE_INFO_GET = "/vulnerability/cve/info/get"
VUL_CVE_HOST_GET = "/vulnerability/cve/host/get"
VUL_CVE_TASK_HOST_GET = "/vulnerability/cve/task/host/get"
VUL_CVE_STATUS_SET = "/vulnerability/cve/status/set"
VUL_CVE_ACTION_QUERY = "/vulnerability/cve/action/query"
VUL_CVE_UPLOAD_ADVISORY = "/vulnerability/cve/advisory/upload"

# route of host related interface
VUL_HOST_SCAN = "/vulnerability/host/scan"
VUL_HOST_STATUS_GET = "/vulnerability/host/status/get"
VUL_HOST_LIST_GET = "/vulnerability/host/list/get"
VUL_HOST_INFO_GET = "/vulnerability/host/info/get"
VUL_HOST_CVE_GET = "/vulnerability/host/cve/get"

# route of task related interface
VUL_TASK_LIST_GET = "/vulnerability/task/list/get"
VUL_TASK_PROGRESS_GET = "/vulnerability/task/progress/get"
VUL_TASK_INFO_GET = "/vulnerability/task/info/get"
VUL_TASK_CVE_GENERATE = "/vulnerability/task/cve/generate"
VUL_TASK_CVE_INFO_GET = "/vulnerability/task/cve/info/get"
VUL_TASK_CVE_STATUS_GET = "/vulnerability/task/cve/status/get"
VUL_TASK_CVE_PROGRESS_GET = "/vulnerability/task/cve/progress/get"
VUL_TASK_CVE_RESULT_GET = "/vulnerability/task/cve/result/get"
VUL_TASk_EXECUTE = "/vulnerability/task/execute"
VUL_TASK_CVE_ROLLBACK = "/vulnerability/task/cve/rollback"
VUL_TASK_REPO_GENERATE = "/vulnerability/task/repo/generate"
VUL_TASK_REPO_INFO_GET = "/vulnerability/task/repo/info/get"
VUL_TASK_REPO_RESULT_GET = "/vulnerability/task/repo/result/get"
VUL_TASK_DELETE = "/vulnerability/task/delete"
VUL_TASK_PLAYBOOK_GET = "/vulnerability/task/playbook/get"


# elasticsearch index
CVE_PKG_INDEX = 'cve_pkg'
TASK_INDEX = "task"


# elasticsearch testcase run flag. NEVER TURN IT TO TRUE IN PRODUCTION ENVIRONMENT.
# The test cases will remove the all the data of the es.
ES_TEST_FLAG = False
