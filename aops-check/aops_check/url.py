#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
Description: url set
"""
from aops_check.conf.constant import (
    QUERY_APP,
    QUERY_APP_LIST,
    CREATE_APP,
    IDENTIFY_SCENE,
    CREATE_WORKFLOW,
    DELETE_WORKFLOW,
    QUERY_WORKFLOW,
    QUERY_WORKFLOW_LIST,
    UPDATE_WORKFLOW,
    IF_HOST_IN_WORKFLOW,
    QUERY_MODEL_LIST,
    QUERY_ALGO_LIST,
    QUERY_ALGO,
    QUERY_HOST_CHECK_RESULT,
    QUERY_HOST_CHECK_RESULT_LIST,
    QUERY_RESULT_TOTAL_COUNT,
    CHECK_RESULT_CONFIRM,
    QUERY_DOMAIN_COUNT,
    DOWNLOAD_HOST_CHECK_RESULT,
)
from aops_check.controllers import (
    app_controller,
    scene_controller,
    workflow_controller,
    model_controller,
    algorithm_controller,
    result_controller
)

URLS = []

SPECIFIC_URLS = {
    'APP_URLS': [
        (app_controller.CreateApp, CREATE_APP),
        (app_controller.QueryApp, QUERY_APP),
        (app_controller.QueryAppList, QUERY_APP_LIST)
    ],
    'SCENE_URLS': [
        (scene_controller.RecognizeScene, IDENTIFY_SCENE)
    ],
    'WORKFLOW_URLS': [
        (workflow_controller.CreateWorkflow, CREATE_WORKFLOW),
        (workflow_controller.DeleteWorkflow, DELETE_WORKFLOW),
        (workflow_controller.QueryWorkflow, QUERY_WORKFLOW),
        (workflow_controller.QueryWorkflowList, QUERY_WORKFLOW_LIST),
        (workflow_controller.UpdateWorkflow, UPDATE_WORKFLOW),
        (workflow_controller.IfHostInWorkflow, IF_HOST_IN_WORKFLOW)
    ],
    'MODEL_URLS': [
        (model_controller.QueryModelList, QUERY_MODEL_LIST)
    ],
    'ALGORITHM': [
        (algorithm_controller.QueryAlgorithmList, QUERY_ALGO_LIST),
        (algorithm_controller.QueryAlgorithm, QUERY_ALGO)
    ],
    'RESULT': [
        (result_controller.QueryCheckResultHost, QUERY_HOST_CHECK_RESULT),
        (result_controller.QueryCheckResultList, QUERY_HOST_CHECK_RESULT_LIST),
        (result_controller.QueryResultTotalCount, QUERY_RESULT_TOTAL_COUNT),
        (result_controller.ConfirmCheckResult, CHECK_RESULT_CONFIRM),
        (result_controller.QueryDomainResultCount, QUERY_DOMAIN_COUNT),
        (result_controller.DownloadAlertReport, DOWNLOAD_HOST_CHECK_RESULT),
    ]
}

for _, value in SPECIFIC_URLS.items():
    URLS.extend(value)
