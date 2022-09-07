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
from sqlalchemy.sql.sqltypes import Integer, String, Float, Boolean
from aops_utils.database.table import Base, MyBase
from aops_utils.database.helper import create_tables
from aops_check.database import ENGINE


class WorkflowHostAssociation(Base, MyBase):
    """
    workflow and host tables' association table, record host and workflow's association
    """
    __tablename__ = "workflow_host"

    host_id = Column(String(32), primary_key=True, nullable=False)
    host_name = Column(String(20), nullable=False)
    host_ip = Column(String(16), nullable=False)
    workflow_id = Column(String(32), ForeignKey('workflow.workflow_id', ondelete="CASCADE"),
                         primary_key=True)


class Workflow(Base, MyBase):
    """
    workflow info Table
    """
    __tablename__ = "workflow"

    workflow_id = Column(String(32), primary_key=True, nullable=False)
    workflow_name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    create_time = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    app_name = Column(String(20), nullable=False)
    app_id = Column(String(32), nullable=False)
    step = Column(Integer)
    period = Column(Integer)
    domain = Column(String(20))

    username = Column(String(40))


class Algorithm(Base, MyBase):
    """
    algorithm info
    """
    __tablename__ = "algorithm"

    algo_id = Column(String(32), primary_key=True, nullable=False)
    algo_name = Column(String(50))
    field = Column(String(50), nullable=True)
    description = Column(String(100), nullable=True)
    path = Column(String(150), nullable=False)

    username = Column(String(40), nullable=False)


class Model(Base, MyBase):
    """
    Model info
    """
    __tablename__ = "model"

    model_id = Column(String(32), primary_key=True, nullable=False)
    model_name = Column(String(20), nullable=False)
    tag = Column(String(255), nullable=True)
    algo_id = Column(String(32), ForeignKey(
        'algorithm.algo_id'), nullable=False)
    create_time = Column(Integer, nullable=False)
    file_path = Column(String(64), nullable=True)
    precision = Column(Float, nullable=True)

    username = Column(String(40), nullable=False)


class DomainCheckResult(Base, MyBase):
    """
    domain check result
    """
    __tablename__ = "domain_check_result"

    alert_id = Column(String(32), primary_key=True, nullable=False)
    domain = Column(String(20), nullable=False)
    alert_name = Column(String(50))
    time = Column(Integer, nullable=False)
    workflow_name = Column(String(50), nullable=False)
    workflow_id = Column(String(32), nullable=False)
    username = Column(String(20), nullable=True)
    level = Column(String(20), nullable=True)
    confirmed = Column(Boolean, default=False)


class AlertHost(Base, MyBase):
    """
    Alert host relationship
    """
    __tablename__ = "alert_host"

    host_id = Column(String(32), primary_key=True)
    alert_id = Column(String(32), ForeignKey('domain_check_result.alert_id', ondelete="CASCADE"),
                      primary_key=True)
    host_ip = Column(String(32), nullable=False)
    host_name = Column(String(50), nullable=False)


class HostCheckResult(Base, MyBase):
    """
    Host check result
    """
    __tablename__ = "host_check_result"

    id = Column(Integer, autoincrement=True, primary_key=True)
    host_id = Column(String(32), ForeignKey(
        'alert_host.host_id', ondelete="CASCADE"))
    time = Column(Integer, nullable=False)
    is_root = Column(Boolean, default=False)
    metric_name = Column(String(50))
    metric_label = Column(String(255))


def create_check_tables(engine=ENGINE):
    """
    create check tables of aops-check service
    Args:
        engine: mysql engine

    Returns:

    """
    # pay attention, the sequence of list is important. Base table need to be listed first.
    tables = [Workflow, WorkflowHostAssociation, Algorithm,
              Model, DomainCheckResult, HostCheckResult, AlertHost]
    tables_objects = [Base.metadata.tables[table.__tablename__]
                      for table in tables]
    create_tables(Base, engine, tables=tables_objects)
