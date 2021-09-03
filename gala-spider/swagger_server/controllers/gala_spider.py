import connexion
import six

from swagger_server.models.base_response import BaseResponse  # noqa: E501
from swagger_server.models.entities_response import EntitiesResponse  # noqa: E501
from swagger_server import util


def get_observed_entity_list(timestamp=None):  # noqa: E501
    """get observed entity list

    get observed entity list # noqa: E501

    :param timestamp: the time that cared
    :type timestamp: int

    :rtype: EntitiesResponse
    """
    return 'do some magic!'


def get_topo_graph_status():  # noqa: E501
    """get Topo Graph Engine Service health status

    get Topo Graph Engine Service health status # noqa: E501


    :rtype: BaseResponse
    """
    return 'do some magic!'
