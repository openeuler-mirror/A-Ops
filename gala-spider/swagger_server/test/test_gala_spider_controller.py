# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.base_response import BaseResponse  # noqa: E501
from swagger_server.models.entities_response import EntitiesResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestGalaSpiderController(BaseTestCase):
    """GalaSpiderController integration test stubs"""

    def test_get_observed_entity_list(self):
        """Test case for get_observed_entity_list

        get observed entity list
        """
        query_string = [('timestamp', 789)]
        response = self.client.open(
            '/gala-spider/api/v1/get_entities',
            method='GET',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_topo_graph_status(self):
        """Test case for get_topo_graph_status

        get Topo Graph Engine Service health status
        """
        response = self.client.open(
            '/gala-spider/api/v1/get_status',
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
