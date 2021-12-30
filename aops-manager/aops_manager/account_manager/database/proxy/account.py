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
Time: 2021-12-22 10:37:56
Author: peixiaochao
Description: 
"""
import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash

from aops_manager.account_manager.key import HostKey
from aops_utils.log.log import LOGGER
from aops_utils.restful.status import DATABASE_INSERT_ERROR, DATABASE_QUERY_ERROR, \
    LOGIN_ERROR, REPEAT_PASSWORD, SUCCEED
from aops_manager.function.verify.acount import CertificateSchema
from aops_utils.restful.response import MyResponse
from aops_utils.database.proxy import MysqlProxy
from aops_utils.database.table import User


class UserDatabase(MysqlProxy):
    """
    User related table operation
    """

    def add_user(self, data):
        """
        Setup user

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx
                }

        Returns:
            int: status code
        """
        username = data.get('username')
        password = data.get('password')
        password_hash = User.hash_password(password)
        user = User(username=username, password=password_hash)

        try:
            self.session.add(user)
            self.session.commit()
            LOGGER.info("add user succeed")
            return SUCCEED

        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            self.session.rollback()
            return DATABASE_INSERT_ERROR

    def login(self, data):
        """
        Check user login

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx
                }

        Returns:
            int: status code
        """
        username = data.get('username')
        password = data.get('password')

        try:
            query_res = self.session.query(
                User).filter_by(username=username).all()
            if len(query_res) == 0:
                LOGGER.error("login with unknown username")
                return LOGIN_ERROR

            self.session.commit()
            res = User.check_hash_password(query_res[0].password, password)

            if res:
                LOGGER.info("user login succeed")
                return SUCCEED

            LOGGER.error("login with wrong password")
            return LOGIN_ERROR

        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            return DATABASE_QUERY_ERROR

    def change_password(self, data):
        """
        Change user password

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx
                }

        Returns:
            int: status code
        """
        username = data.get('username')
        password = data.get('password')

        try:
            password_hash = generate_password_hash(password)
            query_res = self.session.query(
                User).filter_by(username=username).all()
            if len(query_res) == 0:
                LOGGER.error("login with unknown username")
                return LOGIN_ERROR

            user = query_res[0]
            if check_password_hash(user.password, password):
                return REPEAT_PASSWORD

            user.password = password_hash
            self.session.commit()
            LOGGER.error("change password succeed")
            return SUCCEED

        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("change password fail")
            return DATABASE_QUERY_ERROR

    def certificate(self, data):
        """
        certificate user token
        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx",
                    "token": "xxxx",
                }

        Returns:

        """
        access_token = data.get("token")
        verify_res = MyResponse.verify_all(data, CertificateSchema, access_token)
        if verify_res == SUCCEED:
            LOGGER.info("certificate account succeed!")
            HostKey.update(access_token, data['key'])
            return verify_res

        LOGGER.info("fail certificate account!")
        return verify_res
