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
Description: Database proxy
"""
import math
from urllib3.exceptions import LocationValueError
import sqlalchemy
from elasticsearch import Elasticsearch, ElasticsearchException, helpers, TransportError, \
    NotFoundError
from abc import ABC, abstractmethod
from aops_database.conf import configuration
from aops_utils.log.log import LOGGER


class DataBaseProxy(ABC):
    """
    Base proxy
    """

    def __init__(self):
        """
        init
        """

    @abstractmethod
    def connect(self):
        """
        proxy should implement connect function
        """

    @abstractmethod
    def close(self):
        """
        proxy should implement close function
        """


class ElasticsearchProxy(DataBaseProxy):
    """
    Elasticsearch proxy
    """

    def __init__(self, host=None, port=None):
        """
        Instance initialization

        Args:
            host(str)
            port(int)
        """
        self._host = host or configuration.elasticsearch.get(
            'IP')  # pylint: disable=E1101
        self._port = port or configuration.elasticsearch.get(
            'PORT')  # pylint: disable=E1101
        self.connected = False
        self._es_db = None
        super().__init__()

    def connect(self):
        """
        Connect to elasticsearch server

        Returns:
            bool
        """
        try:
            self._es_db = Elasticsearch(
                [{"host": self._host, "port": self._port, "timeout": 150}])
            self._es_db.info()
            self.connected = True
        except (LocationValueError, ElasticsearchException):
            LOGGER.error("Elasticsearch connection failed.")

        return self.connected

    def __del__(self):
        """
        Close connection
        """
        self.close()

    def close(self):
        """
        Close db connect
        """
        if not self.connected:
            return

        if self._es_db:
            self._es_db.close()

    def query(self, index, body, source=True):
        """
        query the index

        args:
            index(str): index of the data
            body(dict): query body
            source(list or bool): list of source

        Returns:
            bool: succeed or fail
            list: result of query
        """
        result = []
        try:
            result = self._es_db.search(index=index,  # pylint: disable=E1123
                                        body=body,
                                        _source=source)
            return True, result

        except NotFoundError as error:
            LOGGER.warning(error)
            return True, result

        except ElasticsearchException as error:
            LOGGER.error(error)
            return False, result

    def scan(self, index, body, source=True):
        """
        Batch query function

        Args:
            index(str): index of the data
            body(dict): query body
            source(list or bool): list of source

        Returns:
            bool: succeed or fail
            list: result of query
        """
        result = []
        try:
            temp = helpers.scan(
                client=self._es_db, index=index, query=body,
                scroll='5m', timeout='1m', _source=source)
            for res in temp:
                result.append(res['_source'])
            return True, result

        except NotFoundError as error:
            LOGGER.warning(error)
            return True, result

        except ElasticsearchException as error:
            LOGGER.error(error)
            return False, result

    def count(self, index, body):
        """
        Get count of index

        Args:
            index(str): index of the data
            body(dict): query body

        Returns:
            bool: succeed or fail
            int: count
        """
        try:
            count = self._es_db.count(index=index, body=body).get("count", 0)
            return True, count
        except ElasticsearchException as error:
            LOGGER.error(error)
            return False, 0

    def create_index(self, index, body):
        """
        Create table

        Args:
            index(str)
            body(dict)

        Returns:
            bool: succeed or fail
        """
        try:
            if not self._es_db.indices.exists(index):
                self._es_db.indices.create(index=index, body=body)
        except ElasticsearchException as error:
            LOGGER.error(error)
            LOGGER.error("Create index fail")
            return False
        return True

    def insert(self, index, body, doc_type="_doc"):
        """
        Insert data to the index

        Args:
            doc_type(str): doc_type of the document will be insert
            index(str): index will be operated
            body(dict): body will be insert

        Returns:
            bool
        """
        try:
            self._es_db.index(index=index,
                              doc_type=doc_type,
                              body=body)
            return True
        except ElasticsearchException as error:
            LOGGER.error(error)
            return False

    def _bulk(self, action):
        """
        Do bulk action

        Args:
            action(list): actions

        Returns:
            bool
        """
        try:
            if action:
                helpers.bulk(self._es_db, action)
            return True
        except ElasticsearchException as error:
            LOGGER.error(error)
            return False

    def insert_bulk(self, index, data):
        """
        Insert batch data into es

        Args:
            index(str): index of the data
            data(list): batch data

        Returns:
            bool: succeed or fail
        """
        action = []
        for item in data:
            action.append({
                "_index": index,
                "_source": item})

        return self._bulk(action)

    def update_bulk(self, index, data):
        """
        Update batch data

        Args:
            index(str): index of the data
            data(list): batch data

        Returns:
            bool: succeed or fail
        """
        action = []
        for item in data:
            _id = item.get("_id")
            doc = item.get("doc")
            action.append({
                "_op_type": "update",
                "_index": index,
                "_id": _id,
                "doc": doc
            })

        return self._bulk(action)

    def delete(self, index, body):
        """
        Delete data

        Args:
            index(str): index will be operated
            body(dict): dict query body

        Returns:
            bool
        """

        try:
            self._es_db.delete_by_query(index=index, body=body)
            return True
        except ElasticsearchException as error:
            LOGGER.error(str(error))
        return False

    def delete_index(self, index):
        """
        Delete index

        Args:
            index(str)

        Returns:
            bool
        """
        try:
            self._es_db.indices.delete(index)
            return True
        except TransportError:
            LOGGER.error("delete es index %s fail", index)
            return False

    @staticmethod
    def _make_es_paginate_body(data, count, body):
        """
        Make a body that can query es by direction or do paginate

        Args:
            data(dict): parameter
            count(int): total count
            body(dict): origin query body

        Returns:
            int: total page
        """

        total_page = 1

        page = data.get('page')
        per_page = data.get('per_page')
        if page and per_page:
            total_page = math.ceil(count / per_page)
            start = (page - 1) * per_page
            body.update({"from": start, "size": per_page})

        sort = data.get('sort')
        direction = data.get('direction') or 'asc'
        if sort and direction:
            body.update(
                {"sort": [{sort: {"order": direction, "unmapped_type": "keyword"}}]})

        return total_page

    @staticmethod
    def _general_body(data):
        """
        Generate general body

        Args:
            data(dict)

        Returns:
            dict
        """
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"username": data.get("username")}}
                    ]
                }
            }
        }
        return query_body


class MysqlProxy(DataBaseProxy):
    """
    Proxy of mysql
    """

    def __init__(self, host=None, port=None):
        """
        Class instance initialization

        Args:
            host(str)
            port(int)
        """
        self.host = host
        self.port = port
        self.session = None
        super().__init__()

    def connect(self, session):  # pylint: disable=W0221
        """
        Make a connect to database connection pool

        Args:
            session(session): database connection session

        Returns:
            bool: connect succeed or fail
        """
        try:
            self.session = session()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            return False

        return True

    def __del__(self):
        """
        Close connection
        """
        self.close()

    def close(self):
        """
        Close connection
        """
        if self.session:
            self.session.close()

    def insert(self, table, data):
        """
        Insert data to table

        Args:
            table(class): table of database
            data(dict): inserted data

        Returns:
            bool: insert succeed or fail
        """
        try:
            self.session.add(table(**data))
            self.session.commit()
            return True

        except sqlalchemy.exc.SQLAlchemyError as error:
            self.session.rollback()
            LOGGER.error(error)
            return False

    def select(self, table, condition):
        """
        Query data from table

        Args:
            table(list): table or field list of database
            condition(dict): query condition

        Returns:
            bool: query succeed or fail
        """
        try:
            data = self.session.query(*table).filter_by(**condition).all()
            return True, data
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            return False, []

    def delete(self, table, condition):
        """
        Delete data from table

        Args:
            table(class): table of database
            condition(dict): delete condition

        Returns:
            bool: delete succeed or fail
        """
        try:
            self.session.query(table).filter_by(**condition).delete()
            self.session.commit()
            return True

        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            self.session.rollback()
            return False
