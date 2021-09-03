# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.call import Call
from swagger_server.models.runon import Runon
from swagger_server import util


class Dependenceitem(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, calls: List[Call]=None, run_ons: List[Runon]=None):  # noqa: E501
        """Dependenceitem - a model defined in Swagger

        :param calls: The calls of this Dependenceitem.  # noqa: E501
        :type calls: List[Call]
        :param run_ons: The run_ons of this Dependenceitem.  # noqa: E501
        :type run_ons: List[Runon]
        """
        self.swagger_types = {
            'calls': List[Call],
            'run_ons': List[Runon]
        }

        self.attribute_map = {
            'calls': 'calls',
            'run_ons': 'runOns'
        }

        self._calls = calls
        self._run_ons = run_ons

    @classmethod
    def from_dict(cls, dikt) -> 'Dependenceitem':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Dependenceitem of this Dependenceitem.  # noqa: E501
        :rtype: Dependenceitem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def calls(self) -> List[Call]:
        """Gets the calls of this Dependenceitem.


        :return: The calls of this Dependenceitem.
        :rtype: List[Call]
        """
        return self._calls

    @calls.setter
    def calls(self, calls: List[Call]):
        """Sets the calls of this Dependenceitem.


        :param calls: The calls of this Dependenceitem.
        :type calls: List[Call]
        """

        self._calls = calls

    @property
    def run_ons(self) -> List[Runon]:
        """Gets the run_ons of this Dependenceitem.


        :return: The run_ons of this Dependenceitem.
        :rtype: List[Runon]
        """
        return self._run_ons

    @run_ons.setter
    def run_ons(self, run_ons: List[Runon]):
        """Sets the run_ons of this Dependenceitem.


        :param run_ons: The run_ons of this Dependenceitem.
        :type run_ons: List[Runon]
        """

        self._run_ons = run_ons
