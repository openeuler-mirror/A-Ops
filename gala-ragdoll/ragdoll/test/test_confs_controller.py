# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.conf_host import ConfHost  # noqa: E501
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.excepted_conf_info import ExceptedConfInfo  # noqa: E501
from ragdoll.models.expected_conf import ExpectedConf  # noqa: E501
from ragdoll.models.real_conf_info import RealConfInfo  # noqa: E501
from ragdoll.models.sync_status import SyncStatus  # noqa: E501
from ragdoll.models.path import Path
from ragdoll.test import BaseTestCase


class TestConfsController(BaseTestCase):
    """ConfsController integration test stubs"""

    def test_get_the_sync_status_of_domain(self):
        """Test case for get_the_sync_status_of_domain

        get the status of the domain
        """
        body = DomainName(domain_name = "dnf")
        response = self.client.open(
            '/confs/getDomainStatus',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("response is : {}".format(response.data.decode('utf-8')))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_query_excepted_confs(self):
        """Test case for query_excepted_confs

        query expected configuration value in the current hostId node
        """
        response = self.client.open(
            '/confs/queryExpectedConfs',
            method='POST')

        print("response is : {}".format(response.data.decode('utf-8')))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_query_real_confs(self):
        """Test case for query_real_confs

        query the real configuration value in the current hostId node
        """

        hostID1 = {
            "hostId" : '551d02da-7d8c-4357-b88d-15dc55ee22ss'
        }
        # hostID2 = {
        #     "hostId" : '551d02da-7d8c-4357-b88d-15dc55ee22cc'
        # }
        body = ConfHost(domain_name = "dnf", host_ids = [hostID1])
        response = self.client.open(
            '/confs/queryRealConfs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("test_query_real_confs response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sync_conf_to_host_from_domain(self):
        """Test case for sync_conf_to_host_from_domain

        synchronize the configuration information of the configuration domain to the host
        """
        hostID1 = {
            "hostId" : '551d02da-7d8c-4357-b88d-15dc55ee22ss'
        }
        body = ConfHost(domain_name = "dnf",
                        host_ids = [hostID1])

        response = self.client.open(
            '/confs/syncConf',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        print("test_sync_conf_to_host_from_domain response is : {}".format(response.data.decode('utf-8')))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
