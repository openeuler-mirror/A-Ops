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
Description:
"""
import unittest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from werkzeug.security import generate_password_hash

from aops_utils.database.table import Host, User, Base, create_utils_tables
from aops_utils.database.helper import drop_tables, create_database_engine
from aops_utils.restful.status import DATA_EXIST, PARTIAL_SUCCEED, SUCCEED, DATA_DEPENDENCY_ERROR, DATABASE_INSERT_ERROR, NO_DATA
from aops_utils.compare import compare_two_object
from aops_manager.database.proxy.host import HostProxy


class TestHostDatabase(unittest.TestCase):
    def setUp(self):
        # create engine to database
        self.proxy = HostProxy()
        mysql_host = "127.0.0.1"
        mysql_port = 3306
        mysql_url_format = "mysql+pymysql://@%s:%s/%s"
        mysql_database_name = "aops_test"
        engine_url = mysql_url_format % (
            mysql_host, mysql_port, mysql_database_name)
        self.engine = create_database_engine(engine_url, 100, 7200)
        session = scoped_session(sessionmaker(bind=self.engine))
        self.proxy.connect(session)
        # create all tables
        create_utils_tables(Base, self.engine)
        # create user
        data = {
            "username": "admin",
            "password": "123456"
        }
        password_hash = generate_password_hash(data['password'])
        token = ""
        user = User(username=data['username'],
                    password=password_hash, token=token)
        self.proxy.session.add(user)
        self.proxy.session.commit()

    def tearDown(self):
        self.proxy.close()
        drop_tables(Base, self.engine)

    def test_api_host_group(self):
        # ==============add host group===================
        group_data1 = {
            "username": "admin",
            "host_group_name": "group1",
            "description": "xxx"
        }
        group_data2 = {
            "username": "admin",
            "host_group_name": "group2",
            "description": "xxx",
            # "host_count": 3
        }
        group_data3 = {
            "username": "admin",
            "host_group_name": "group3",
            "description": "xxx",
            # "host_count": 1
        }
        group_data4 = {
            "username": "admin",
            "host_group_name": "group1",
            "description": "xxx",
        }
        host=[{
            "username": "admin",
            "host_name": "host1",
            "host_group_name": "group2",
            "host_id": "id1",
            "public_ip": "127.0.0.1",
            "management": False,
            "agent_port": 1122
        },
         {
            "username": "admin",
            "host_name": "host2",
            "host_group_name": "group2",
            "host_id": "id2",
            "public_ip": "127.0.0.2",
            "management": False,
            "agent_port": 1122
        },
        {
            "username": "admin",
            "host_name": "host3",
            "host_group_name": "group2",
            "host_id": "id3",
            "public_ip": "127.0.0.3",
            "management": False,
            "agent_port": 1122
        },
        {
            "username": "admin",
            "host_name": "host4",
            "host_group_name": "group3",
            "host_id": "id4",
            "public_ip": "127.0.0.4",
            "management": False,
            "agent_port": 1122
        }]

        res = self.proxy.add_host_group(group_data1)
        self.assertEqual(res, SUCCEED)
        res = self.proxy.add_host_group(group_data3)
        self.assertEqual(res, SUCCEED)
        res = self.proxy.add_host_group(group_data2)
        self.assertEqual(res, SUCCEED)
        res = self.proxy.add_host_group(group_data4)
        self.assertEqual(res, DATA_EXIST)
        for data in host:
            self.proxy.add_host(data)
        # ==============get host group=================
        args = {
            "username": "admin",
            "sort": "host_group_name"
        }
        expected_res = [
            {
                'host_group_name': 'group1',
                'description': 'xxx',
                'host_count': 0
            },
            {
                'host_group_name': 'group2',
                'description': 'xxx',
                'host_count': 3
            },
            {
                'host_group_name': 'group3',
                'description': 'xxx',
                'host_count': 1
            }
        ]
        res = self.proxy.get_host_group(args)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(res[1]['host_group_infos'], expected_res)

        args = {
            "username": "admin",
            "sort": "host_count",
            "direction": "desc",
            "page": 2,
            "per_page": 2
        }
        expected_res = [
            {
                'host_group_name': 'group1',
                'description': 'xxx',
                'host_count': 0
            }
        ]
        res = self.proxy.get_host_group(args)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(res[1]['host_group_infos'], expected_res)

        args = {
            "username": "admin",
            "sort": "host_count",
            "direction": "desc"
        }
        expected_res = [
            {
                'host_group_name': 'group2',
                'description': 'xxx',
                'host_count': 3
            },
            {
                'host_group_name': 'group3',
                'description': 'xxx',
                'host_count': 1
            },
            {
                'host_group_name': 'group1',
                'description': 'xxx',
                'host_count': 0
            }
        ]
        res = self.proxy.get_host_group(args)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(res[1]['host_group_infos'], expected_res)

        # ===============delete host group=============
        args = {
            "host_group_list": ["group2"],
            "username": "admin"
        }
        res = self.proxy.delete_host_group(args)

        self.assertEqual(res[1]['deleted'], [])
        self.assertEqual(res[0], DATA_DEPENDENCY_ERROR)

        args = {
            "host_group_list": ["group1"],
            "username": "admin"
        }
        res = self.proxy.delete_host_group(args)

        self.assertEqual(res[1]['deleted'], ["group1"])

    def test_api_host(self):
        # ==============add host group===================
        group_data1 = {
            "username": "admin",
            "host_group_name": "group1",
            "description": "xxx"
        }
        group_data2 = {
            "username": "admin",
            "host_group_name": "group2",
            "description": "xxx",
            # "host_count": 0
        }
        self.proxy.add_host_group(group_data1)
        self.proxy.add_host_group(group_data2)

        # ==============add host===================
        data = [
            {
                "host_name": "host1",
                "host_group_name": "group1",
                "host_id": "id1",
                "public_ip": "127.0.0.1",
                "management": False,
                "username": "admin",
                "agent_port": 1111
            },
            {
                "host_name": "host2",
                "host_group_name": "group1",
                "host_id": "id2",
                "public_ip": "127.0.0.2",
                "management": True,
                "username": "admin",
                "agent_port": 1111
            },
            {
                "host_name": "host3",
                "host_group_name": "group2",
                "host_id": "id3",
                "public_ip": "127.0.0.3",
                "management": False,
                "username": "admin",
                "agent_port": 1111
            },
            {
                "host_name": "host4",
                "host_group_name": "group2",
                "host_id": "id4",
                "public_ip": "127.0.0.4",
                "management": True,
                "username": "admin",
                "agent_port": 1111
            },
            {
                "host_name": "host5",
                "host_group_name": "group2",
                "host_id": "id5",
                "public_ip": "127.0.0.5",
                "management": False,
                "username": "admin",
                "agent_port": 1111
            }
        ]
        for host in data:
            res = self.proxy.add_host(host)
            self.assertEqual(res, SUCCEED)

        condition = {}
        res = self.proxy.select([Host], condition)
        self.assertEqual(5, len(res[1]))

        args = {
            "username": "admin"
        }
        expected_res = [
            {
                'host_group_name': 'group1',
                'description': 'xxx',
                'host_count': 2
            },
            {
                'host_group_name': 'group2',
                'description': 'xxx',
                'host_count': 3
            }
        ]
        res = self.proxy.get_host_group(args)
        self.assertEqual(res[0], SUCCEED)
        self.assertEqual(res[1]['host_group_infos'], expected_res)

        # no such host group
        data = {
            "host_name": "host1",
            "host_group_name": "group99",
            "host_id": "id1",
            "public_ip": "127.0.0.1",
            "management": False,
            "username": "admin",
            "agent_port": 1111
        }
        res = self.proxy.add_host(data)
        self.assertEqual(res, NO_DATA)

        # existed host
        data = {
            "host_name": "host1",
            "host_group_name": "group1",
            "host_id": "id1",
            "public_ip": "127.0.0.1",
            "management": False,
            "username": "admin",
            "agent_port": 1111
        }
        res = self.proxy.add_host(data)
        self.assertEqual(res, DATA_EXIST)

        # ==============get host=====================
        args = {
            "host_group_list": [],
            "sort": "host_name",
            "direction": "desc",
            "page": 1,
            "per_page": 2,
            "username": "admin"
        }

        res = self.proxy.get_host(args)
        expected_res = [
            {
                "host_id": "id5",
                "host_name": "host5",
                "host_group_name": "group2",
                "public_ip": "127.0.0.5",
                "management": False,
                "status": None,
                "scene": None,
            },
            {
                "host_id": "id4",
                "host_name": "host4",
                "host_group_name": "group2",
                "public_ip": "127.0.0.4",
                "management": True,
                "status": None,
                "scene": None
            }
        ]
        self.assertEqual(res[1]['total_count'], 5)
        self.assertEqual(res[1]['host_infos'], expected_res)

        args = {
            "host_group_list": [],
            "sort": "host_name",
            "direction": "asc",
            "page": 2,
            "per_page": 2,
            "username": "admin"
        }

        res = self.proxy.get_host(args)
        expected_res = [
            {
                "host_id": "id3",
                "host_name": "host3",
                "host_group_name": "group2",
                "public_ip": "127.0.0.3",
                "management": False,
                "status": None,
                "scene": None
            },
            {
                "host_id": "id4",
                "host_name": "host4",
                "host_group_name": "group2",
                "public_ip": "127.0.0.4",
                "management": True,
                "status": None,
                "scene": None
            }
        ]
        self.assertEqual(res[1]['total_count'], 5)
        self.assertEqual(res[1]['host_infos'], expected_res)

        # ===============get host count================
        args = {
            "username": "admin"
        }
        expected_res = 5
        res = self.proxy.get_host_count(args)
        self.assertEqual(expected_res, res[1]["host_count"])

        # ================get host info=================
        args = {
            "username": "admin",
            "host_list": ["id1", "id2"]
        }
        expected_res = [
            {
                "host_name": "host1",
                "host_group_name": "group1",
                "host_id": "id1",
                "public_ip": "127.0.0.1",
                "management": False,
                "status": None,
                "scene": None,
                "agent_port": 1111
            },
            {
                "host_name": "host2",
                "host_group_name": "group1",
                "host_id": "id2",
                "public_ip": "127.0.0.2",
                "management": True,
                "status": None,
                "scene": None,
                "agent_port": 1111
            }
        ]
        res = self.proxy.get_host_info(args)
        self.assertTrue(compare_two_object(expected_res, res[1]['host_infos']))

        # =====================get host info by user===============
        args = {
        }
        expected_res = {
            "admin": [
                {
                    "host_name": "host1",
                    "host_group_name": "group1",
                    "host_id": "id1",
                    "public_ip": "127.0.0.1"
                },
                {
                    "host_name": "host2",
                    "host_group_name": "group1",
                    "host_id": "id2",
                    "public_ip": "127.0.0.2"
                },
                {
                    "host_name": "host3",
                    "host_group_name": "group2",
                    "host_id": "id3",
                    "public_ip": "127.0.0.3"
                },
                {
                    "host_name": "host4",
                    "host_group_name": "group2",
                    "host_id": "id4",
                    "public_ip": "127.0.0.4"
                },
                {
                    "host_name": "host5",
                    "host_group_name": "group2",
                    "host_id": "id5",
                    "public_ip": "127.0.0.5"
                }
            ]
        }
        res = self.proxy.get_total_host_info_by_user(args)
        self.assertTrue(compare_two_object(expected_res, res[1]['host_infos']))

        # ==============delete host===================
        args = {
            "username": "admin",
            "host_list": ["id1", "id9"]
        }
        res = self.proxy.delete_host(args)
        self.assertEqual(res[0], PARTIAL_SUCCEED)
        self.assertEqual(res[1]["fail_list"][0], "id9")
        self.assertEqual(res[1]['succeed_list'][0], "id1")

        args = {
            "host_group_list": ["group1"],
            "username": "admin"
        }
        res = self.proxy.get_host(args)
        self.assertEqual(res[1]['total_count'], 1)
