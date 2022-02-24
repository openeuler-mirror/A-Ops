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
import unittest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from aops_utils.database.proxy import MysqlProxy
from aops_utils.database.helper import create_database_engine
from aops_utils.tests.test_database.for_mysql.models import Base, Test

class TestMysqlProxy(unittest.TestCase):
    def setUp(self):
        mysql_host = "127.0.0.1"
        mysql_port = 3306
        mysql_url_format = "mysql+pymysql://@%s:%s/%s"
        mysql_database_name = "aops_test"
        engine_url = mysql_url_format % (mysql_host, mysql_port, mysql_database_name)
        self.engine = create_database_engine(engine_url, 100, 7200)
        session = scoped_session(sessionmaker(bind=self.engine))
        self.mysql_proxy = MysqlProxy()
        self.mysql_proxy.connect(session)
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.mysql_proxy.close()
        Base.metadata.drop_all(self.engine)


    def test_operation(self):
        data1 = {
            'name': "Ada",
            "age": 11
        }
        data2 = {
            'age': 13,
            "name": "Bob"
        }
        self.mysql_proxy.insert(Test, data1)
        self.mysql_proxy.insert(Test, data2)

        # test select with condition
        condition = {
            "name": "Bob"
        }
        res = self.mysql_proxy.select([Test.age], condition)
        self.assertEqual(res[1][0][0], 13)

        # test select *
        res = self.mysql_proxy.select([Test], condition={})
        self.assertEqual(len(res[1]), 2)

        # test delete
        condition = {
            "age": 11
        }
        res = self.mysql_proxy.delete(Test, condition)
        self.assertTrue(res)
        res = self.mysql_proxy.select([Test], condition={})
        self.assertEqual(len(res[1]), 1)
