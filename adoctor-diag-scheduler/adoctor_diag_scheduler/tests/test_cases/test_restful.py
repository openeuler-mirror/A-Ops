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
import unittest
from flask import Flask

from aops_utils.conf.constant import DIAG_IMPORT_TREE, DIAG_GET_TASK, DIAG_EXECUTE_DIAG, \
    DIAG_GET_REPORT_LIST, DIAG_GET_TREE, DIAG_DELETE_TREE, DIAG_DELETE_REPORT, DIAG_GET_PROGRESS, \
    DIAG_GET_REPORT

import adoctor_diag_scheduler


param_error = {
    "code": 1000,
    'msg': 'request parameter error'
}

success = {
    "code": 1201,
    'msg': 'the session is invalid'
}

method_error = {
    'message': 'The method is not allowed for the requested URL.'
}


class TestAddDiagTree(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_AddDiagTree_1(self):
        expected_res = param_error
        # normal
        args = {"trees": [{
            "tree_name": "tree1",
            "tree_content": {},
            "description": ""
        }]}
        response = self.client.post(DIAG_IMPORT_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_AddDiagTree_2(self):
        expected_res = param_error
        # normal
        args = {"trees": [{
            "tree_name": "",
            "tree_content": {"name": "tree1"},
            "description": ""
        }]}
        response = self.client.post(DIAG_IMPORT_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_AddDiagTree_3(self):
        expected_res = param_error
        # normal
        args = {"trees": [{
            "tree_name": "",
            "tree_content": {"name": "tree1"},
            "description": ""
        }]}
        response = self.client.post(DIAG_IMPORT_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_AddDiagTree_4(self):
        expected_res = param_error
        # normal
        args = {"trees": []}
        response = self.client.post(DIAG_IMPORT_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_AddDiagTree_5(self):
        expected_res = success
        # normal
        args = {"trees": [{
            "tree_name": "tree1",
            "tree_content": {"name": ""},
            "description": ""
        }]}
        response = self.client.post(DIAG_IMPORT_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_AddDiagTree_6(self):
        expected_res = method_error
        # normal
        args = {"tree_list": []}
        response = self.client.get(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestGetDiagTree(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_GetDiagTree_1(self):
        expected_res = param_error
        # normal
        args = {"tree_list": {}}
        response = self.client.post(DIAG_GET_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTree_2(self):
        expected_res = param_error
        # normal
        args = {"tree_list": ""}
        response = self.client.post(DIAG_GET_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTree_3(self):
        expected_res = success
        # normal
        args = {"tree_list": []}
        response = self.client.post(DIAG_GET_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTree_4(self):
        expected_res = success
        # normal
        args = {"tree_list": [""]}
        response = self.client.post(DIAG_GET_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTree_5(self):
        expected_res = method_error
        # normal
        args = {"tree_list": []}
        response = self.client.get(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestDelDiagTree(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_DelDiagTree_1(self):
        expected_res = param_error
        # normal
        args = {"tree_list": {}}
        response = self.client.delete(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DelDiagTree_2(self):
        expected_res = param_error
        # normal
        args = {"tree_list": ""}
        response = self.client.delete(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DelDiagTree_3(self):
        expected_res = success
        # normal
        args = {"tree_list": []}
        response = self.client.delete(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DelDiagTree_4(self):
        expected_res = success
        # normal
        args = {"tree_list": [""]}
        response = self.client.delete(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DelDiagTree_5(self):
        expected_res = success
        # normal
        args = {"tree_list": [""]}
        response = self.client.delete(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DelDiagTree_6(self):
        expected_res = method_error
        # normal
        args = {"tree_list": []}
        response = self.client.post(DIAG_DELETE_TREE, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestDiagExecute(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_DiagExecute_1(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": [],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "interval": 60
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_2(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111],
            "tree_list": ["tree1", "tree2"],
            "interval": 60
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_3(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": [],
            "interval": 60
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_4(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222, 333],
            "tree_list": ["tree1", "tree2"],
            "interval": 60
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_5(self):
        expected_res = success
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "interval": "60"
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_6(self):
        expected_res = success
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "interval": 60
        }
        response = self.client.post(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DiagExecute_7(self):
        expected_res = method_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "interval": 60
        }
        response = self.client.get(DIAG_EXECUTE_DIAG, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestGetDiagTask(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_GetDiagTask_1(self):
        expected_res = success
        # normal
        args = {
            "time_range": [111, 222]
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_2(self):
        expected_res = param_error
        # normal
        args = {
            "time_range": [111, ]
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_3(self):
        expected_res = param_error
        # normal
        args = {
            "time_range": [111]
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_4(self):
        expected_res = param_error
        # normal
        args = {
            "time_range": [111, 222, 333]
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_5(self):
        expected_res = param_error
        # normal
        args = {
            "time_range": []
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_6(self):
        expected_res = success
        # normal
        args = {
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_7(self):
        expected_res = success
        # normal
        args = {
            "time_range": ["111", "222"]
        }
        response = self.client.post(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetDiagTask_8(self):
        expected_res = method_error
        # normal
        args = {
            "time_range": ["111", "222"]
        }
        response = self.client.get(DIAG_GET_TASK, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestGetProgress(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_GetProgress_1(self):
        expected_res = success
        # normal
        args = {
            "task_list": ["task1"]
        }
        response = self.client.post(DIAG_GET_PROGRESS, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetProgress_2(self):
        expected_res = success
        # normal
        args = {
            "task_list": [""]
        }
        response = self.client.post(DIAG_GET_PROGRESS, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetProgress_3(self):
        expected_res = param_error
        # normal
        args = {
            "task_list": []
        }
        response = self.client.post(DIAG_GET_PROGRESS, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetProgress_4(self):
        expected_res = param_error
        # normal
        args = {
            "task_list": [123, 456]
        }
        response = self.client.post(DIAG_GET_PROGRESS, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetProgress_5(self):
        expected_res = method_error
        # normal
        args = {
            "task_list": ["task1"]
        }
        response = self.client.get(DIAG_GET_PROGRESS, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestGetReport(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_GetReport_1(self):
        expected_res = success
        # normal
        args = {
            "report_list": ["id1"]
        }
        response = self.client.post(DIAG_GET_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReport_2(self):
        expected_res = success
        # normal
        args = {
            "report_list": [""]
        }
        response = self.client.post(DIAG_GET_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReport_3(self):
        expected_res = param_error
        # normal
        args = {
            "report_list": []
        }
        response = self.client.post(DIAG_GET_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReport_4(self):
        expected_res = param_error
        # normal
        args = {
            "report_list": {}
        }
        response = self.client.post(DIAG_GET_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReport_5(self):
        expected_res = method_error
        # normal
        args = {
            "report_list": ["task1"]
        }
        response = self.client.get(DIAG_GET_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestGetReportList(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_GetReportList_1(self):
        expected_res = success
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "page": 1,
            "per_page": 50
        }
        response = self.client.post(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReportList_2(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": ["tree1", "tree2"],
            "page": 1,
            "per_page": 51
        }
        response = self.client.post(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReportList_3(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222, 333],
            "tree_list": ["tree1", "tree2"],
            "page": 1,
            "per_page": 50
        }
        response = self.client.post(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReportList_4(self):
        expected_res = param_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": [111, 222],
            "tree_list": [],
            "page": 1,
            "per_page": -1
        }
        response = self.client.post(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReportList_5(self):
        expected_res = success
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": ["111", "222"],
            "tree_list": [],
            "page": 1,
            "per_page": 2
        }
        response = self.client.post(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_GetReportList_6(self):
        expected_res = method_error
        # normal
        args = {
            "host_list": ["host1"],
            "time_range": ["111", "222"],
            "tree_list": [],
            "page": 1,
            "per_page": 2
        }
        response = self.client.get(DIAG_GET_REPORT_LIST, json=args)
        res = response.json
        self.assertEqual(res, expected_res)


class TestDelReport(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask("adoctor_diag_scheduler")

        for blue, api in adoctor_diag_scheduler.blue_point:
            api.init_app(app)
            app.register_blueprint(blue)

        app.testing = True
        self.client = app.test_client()

    def test_DeleteReport_1(self):
        expected_res = success
        # normal
        args = {
            "report_list": ["id1"]
        }
        response = self.client.delete(DIAG_DELETE_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DeleteReport_2(self):
        expected_res = success
        # normal
        args = {
            "report_list": [""]
        }
        response = self.client.delete(DIAG_DELETE_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DeleteReport_3(self):
        expected_res = success
        # normal
        args = {
            "report_list": []
        }
        response = self.client.delete(DIAG_DELETE_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DeleteReport_4(self):
        expected_res = param_error
        # normal
        args = {
            "report_list": {}
        }
        response = self.client.delete(DIAG_DELETE_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)

    def test_DeleteReport_5(self):
        expected_res = method_error
        # normal
        args = {
            "report_list": ["task1"]
        }
        response = self.client.post(DIAG_DELETE_REPORT, json=args)
        res = response.json
        self.assertEqual(res, expected_res)
