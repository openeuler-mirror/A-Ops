# coding: utf-8

from __future__ import absolute_import

import requests
import http.client
import urllib

from flask import json
from six import BytesIO

from ragdoll.models.base_response import BaseResponse  # noqa: E501
from ragdoll.models.conf import Conf
from ragdoll.models.confs import Confs
from ragdoll.models.domain_manage_conf import DomainManageConf  # noqa: E501
from ragdoll.models.domain_name import DomainName  # noqa: E501
from ragdoll.models.manage_conf import ManageConf
from ragdoll.models.manage_confs import ManageConfs
from ragdoll.test import BaseTestCase


class TestManagementController(BaseTestCase):
    """ManagementController integration test stubs"""

    def test_add_management_confs_in_domain(self):
        """Test case for add_management_confs_in_domain

        add management configuration items and expected values in the domain
        """
        conf1 = Conf(file_path = "/etc/yum.repos.d/openEuler.repo",
                     contents = """
                          [snn]
                          name=snn
                          baseurl=https://repo.huaweicloud.com/openeuler/openEuler-20.03-LTS-SP1/everything/x86_64/
                          enabled=1
                          gpgcheck=0
                          gpgkey=http://repo.openeuler.org/openEuler-20.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler
                        """)
    
        body = Confs(domain_name = "dnf",
                     conf_files = [conf1])
        response = self.client.open(
            '/management/addManagementConf',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_management_confs_in_domain2(self):
        """Test case for add_management_confs_in_domain

        add management configuration items and expected values in the domain
        """
        conf1 = Conf(file_path = "/etc/coremail/coremail.conf",
                     host_id = "551d02da-7d8c-4357-b88d-15dc55ee22ss")
    
        body = Confs(domain_name = "dnf",
                     conf_files = [conf1])
        response = self.client.open(
            '/management/addManagementConf',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


    def test_delete_management_confs_in_domain(self):
        """Test case for delete_management_confs_in_domain

        delete management configuration items and expected values in the domain
        """
        conf = ManageConf(file_path="/etc/yum.repos.d/openEuler.repo")
        body = ManageConfs(domain_name = "dnf",
                           conf_files = [conf])
        response = self.client.open(
            '/management/deleteManagementConf',
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_management_confs_in_domain(self):
        """Test case for get_management_confs_in_domain

        get management configuration items and expected values in the domain
        """
        body = DomainName(domain_name = "dnf")
        response = self.client.open(
            '/management/getManagementConf',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("response is : {}".format(response.data))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_management_confs_in_domain2(self):
        """Test case for get_management_confs_in_domain

        get management configuration items and expected values in the domain
        """
        # params = DomainName(domain_name = "OS")
        url="http://0.0.0.0:8080/management/getManagementConf"
        headers = {"Content-Type": "application/json"}
        #body = {
        #    'domainName': 'OS'
        #}
        body = DomainName(domain_name="OS")
        response = requests.post(url, data=json.dumps(body), headers=headers)  # 发送请求
        print("response is : {}".format(response))
        text = response.text
        print(json.loads(text))

    def test_query_changelog_of_management_confs_in_domain(self):
        """Test case for query_changelog_of_management_confs_in_domain

        query the change log of management config in domain
        """
        conf2 = ManageConf(file_path="/etc/yum.repos.d/openEuler.repo")
        body = ManageConfs(domain_name = "dnf",
                           conf_files = [conf2])
        # body = ManageConfs(domain_name = "dnf",
        #                    conf_files = [])
        response = self.client.open(
            '/management/queryManageConfChange',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        print("response is : {}".format(response))
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

if __name__ == '__main__':
    import unittest
    unittest.main()
