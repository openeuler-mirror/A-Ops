import time
import unittest
from unittest.mock import Mock

from aops_utils.restful.status import SUCCEED, DATA_EXIST, NO_DATA

from aops_check.conf.constant import APP_INDEX
from aops_check.database.dao.app_dao import AppDao
from aops_check.database.factory.mapping import MAPPINGS

test_cases = [
    {
        "username": "test",
        'app_id': "id1",
        "app_name": "name1",
        "description": "we",
        "api": {
            "type": "api",
            "address": "run"
        },
        "detail": {
            "single": {},
            "diag": {}
        }
    },
    {
        "username": "test",
        'app_id': "id2",
        "app_name": "name2",
        "description": "laolu",
        "api": {
            "type": "server",
            "address": "http://127.0.0.1:1122/test"
        },
        "detail": {
        }
    },
    {
        "username": "test",
        'app_id': "id3",
        "app_name": "name3",
        "description": "other",
        "api": {
            "type": "server",
            "address": "http://127.0.0.1:1122/test"
        },
        "detail": {
        }
    },
    {
        "username": "test",
        'app_id': "id4",
        "app_name": "name1",
        "description": "laolu",
        "api": {
            "type": "server",
            "address": "http://127.0.0.1:1122/test"
        },
        "detail": {
        }
    }
]


class AppDaoTestcase(unittest.TestCase):
    def setUp(self) -> None:
        host = "127.0.0.1"
        port = 9200
        self.dao = AppDao(Mock(), host, port)
        self.dao.connect()
        self.index = "app_test_index"
        self.dao.create_index(self.index, MAPPINGS[APP_INDEX])

    def tearDown(self) -> None:
        self.dao.delete_index(self.index)
        self.dao.close()

    def help(self):
        for test_case in test_cases[:-1]:
            self.dao.create_app(test_case, self.index)

        time.sleep(1)

    def test_create_app_should_return_succeed_when_input_is_normal(self):
        res = self.dao.create_app(test_cases[0], self.index)
        self.assertEqual(SUCCEED, res)

    def test_create_app_should_return_data_exist_when_input_existed_app(self):
        res = self.dao.create_app(test_cases[0], self.index)
        self.assertEqual(SUCCEED, res)
        time.sleep(1)
        res = self.dao.create_app(test_cases[-1], self.index)
        self.assertEqual(DATA_EXIST, res)

    def test_query_app_list_should_return_all_result_when_input_is_null(self):
        self.help()
        status, res = self.dao.query_app_list({'username': "test"}, self.index)
        self.assertEqual(SUCCEED, status)
        self.assertEqual(3, res['total_count'])
        self.assertEqual(1, res['total_page'])
        self.assertEqual(3, len(res['app_list']))

    def test_query_app_list_should_return_one_result_when_page_and_per_page_are_defined(self):
        self.help()
        data = {
            "username": "test",
            "page": 2,
            "per_page": 2
        }
        status, res = self.dao.query_app_list(data, self.index)
        self.assertEqual(SUCCEED, status)
        self.assertEqual(3, res['total_count'])
        self.assertEqual(2, res['total_page'])
        self.assertEqual(1, len(res['app_list']))

    def test_query_app_list_should_return_empty_when_username_no_match(self):
        self.help()
        status, res = self.dao.query_app_list({'username': "a"}, self.index)
        self.assertEqual(SUCCEED, status)
        self.assertEqual(0, res['total_count'])
        self.assertEqual(0, res['total_page'])
        self.assertEqual(0, len(res['app_list']))

    def test_query_app_should_return_correct_result_when_input_id_is_correct(self):
        self.help()
        data = {
            'username': "test",
            "app_id": "id3"
        }
        status, res = self.dao.query_app(data, self.index)
        self.assertEqual(SUCCEED, status)
        self.assertEqual(test_cases[2], res['result'])

    def test_query_app_should_return_no_data_when_input_query_app_is_not_existed(self):
        self.help()
        data = {
            'username': "test",
            "app_id": "id5"
        }
        status, res = self.dao.query_app(data, self.index)
        self.assertEqual(NO_DATA, status)


if __name__ == '__main__':
    unittest.main()
