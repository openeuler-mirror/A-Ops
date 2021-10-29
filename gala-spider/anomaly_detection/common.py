import yaml
import os
from spider.util.conf import conf_path


def get_conf_info(path):
    """
    get the threshold of object
    :param path: config path
    :return: dict
    """
    result = {}

    true_path = os.path.realpath(path)
    try:
        with open(true_path, "r") as f:
            result = yaml.safe_load(f.read())
    except IOError:
        print("Anomaly Detection ERROR: Invalid config path!")

    return result

CONF_INFO = get_conf_info(conf_path)

g_edges_list = {"timestamp": 0, "edges_list": {}}
EDGES_LIST_UPDATE_INTERVAL = 60 * 60

class ANOMALY_DETECTION_MODEL_TYPE:
    THRESHOLD_MODEL = "1"
