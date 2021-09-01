# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.host import Host  # noqa: E501
from ragdoll.models.host_infos import HostInfos  # noqa: E501
from ragdoll.test import BaseTestCase


class TestHostController1(BaseTestCase):
    """HostController integration test stubs"""

    def test_add_host_in_domain1(self):
        """Test case for add_host_in_domain

        add host in the configuration domain
        """
        # host1 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ee22ss",
        #              ip = "210.22.22.155")
        host2 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ee22mm",
                     ip = "210.22.22.159")
        body = HostInfos(domain_name = "dnf", host_infos = [host2])
        response = self.client.open(
            '/host/addHost',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("test_add_host_in_domain1 response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_host_in_domain2(self):
        """Test case for add_host_in_domain

        add host in the configuration domain
        """
        host2 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ds22cc",
                     ip = "210.22.22.151",
                     ipv6 = "xxxx")
        host3 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ee22cc",
                     ip = "210.22.22.150")
        body = HostInfos(domain_name = "dnf", host_infos = [host2, host3])
        response = self.client.open(
            '/host/addHost',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("test_add_host_in_domain2 response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_host_in_domain(self):
        """Test case for delete_host_in_domain
        delete host in the configuration  domain
        """
        host2 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ee22mm",
                     ip = "210.22.22.159")
        body = HostInfos(domain_name = "dnf", host_infos = [host2])
        response = self.client.open(
            '/host/deleteHost',
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        print("test_delete_host_in_domain response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_host_in_domain2(self):
        """Test case for delete_host_in_domain

        delete host in the configuration  domain
        """
        host2 = Host(host_id = "551d02da-7d8c-4357-b88d-15dc55ds22cc",
                     ip = "210.22.22.151")
        body = HostInfos(domain_name = "dnf", host_infos = [])
        response = self.client.open(
            '/host/deleteHost',
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        print("test_delete_host_in_domain2 response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_host_by_domain_name(self):
        """Test case for get_host_by_domain_name

        get host by domainName
        """
        body = DomainName(domain_name="dnf")
        response = self.client.open(
            '/host/getHost',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("test_get_host_by_domain_name response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
