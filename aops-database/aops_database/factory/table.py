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
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from aops_utils.database.table import Base,MyBase


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

    def __eq__(self, o):
        return self.user == o.user and (self.host_name == o.host_name or\
            self.public_ip == o.public_ip)


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
