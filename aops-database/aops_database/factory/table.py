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
Description: mysql tables
"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, Integer, String


Base = declarative_base()


class MyBase:  # pylint: disable=R0903
    """
    Class that provide helper function
    """

    def to_dict(self):
        """
        Transfer query data to dict

        Returns:
            dict
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # pylint: disable=E1101


class Host(Base, MyBase):  # pylint: disable=R0903
    """
    Host table
    """
    __tablename__ = "host"

    host_id = Column(String(40), primary_key=True)
    host_name = Column(String(20), nullable=False)
    public_ip = Column(String(16), nullable=False)
    ssh_port = Column(Integer, nullable=False)
    status = Column(String(20))
    management = Column(Boolean, nullable=False)
    host_group_name = Column(String(20))

    user = Column(String(40), ForeignKey('user.username'))
    host_group_id = Column(Integer, ForeignKey('host_group.host_group_id'))

    host_group = relationship('HostGroup', back_populates='hosts')
    owner = relationship('User', back_populates='hosts')


class HostGroup(Base, MyBase):
    """
    Host group table
    """
    __tablename__ = "host_group"

    host_group_id = Column(Integer, autoincrement=True, primary_key=True)
    host_group_name = Column(String(20))
    description = Column(String(60))
    host_count = Column(Integer, default=0)
    username = Column(String(40), ForeignKey('user.username'))

    user = relationship('User', back_populates='host_groups')
    hosts = relationship('Host', back_populates='host_group')

    def __eq__(self, o):
        return self.username == o.username and self.host_group_name == o.host_group_name


class User(Base, MyBase):  # pylint: disable=R0903
    """
    User Table
    """
    __tablename__ = "user"

    username = Column(String(40), primary_key=True)
    password = Column(String(255), nullable=False)

    host_groups = relationship(
        'HostGroup', order_by=HostGroup.host_group_name, back_populates='user')
    hosts = relationship('Host', back_populates='owner')
