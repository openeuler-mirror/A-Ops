# coding: utf-8

from __future__ import absolute_import
import requests
from flask import json
from six import BytesIO

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.domain import Domain  # noqa: E501
from ragdoll.test import BaseTestCase


class TestDomainController1(BaseTestCase):
    """DomainController integration test stubs"""

    def test_create_domain(self):
        """Test case for create_domain

        create domain
        """
        # domain1 = Domain(domain_name = "dnf",
        #                 priority = 0)
        domain2 = Domain(domain_name = "ll",
                        priority = 0)
        body = [domain2]
        response = self.client.open(
            '/domain/createDomain',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')

        print("response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


    def test_delete_domain(self):
        """Test case for delete_domain

        delete domain
        """
        query_string = [('domainName', 'll')]
        response = self.client.open(
            '/domain/deleteDomain',
            method='DELETE',
            query_string=query_string)

        print("response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


    def test_create_domain2(self):
        """Test case for create_domain
        create domain
        """
        url="http://0.0.0.0:8080/domain/createDomain"
        headers = {"Content-Type": "application/json"}
        domain = Domain(domain_name = "ll",
                        priority = 0)
        body = [domain]
        response = requests.post(url, data=json.dumps(body),headers=headers)  # 发送请求
        print("response is : {}".format(response))
        text = response.text
        print(json.loads(text))


    def test_delete_domain2(self):
        """Test case for delete_domain

        delete domain
        """
        url="http://0.0.0.0:8080/domain/deleteDomain?domainName=ll"
        headers = {"Content-Type": "application/json"}
        response = requests.delete(url, headers=headers)  # 发送请求
        print("response is : {}".format(response))
        text = response.text
        print(json.loads(text))


    def test_query_domain(self):
        """Test case for query_domain

        query the list of all configuration domain
        """
        response = self.client.open(
            '/domain/queryDomain',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
