import yaml
from spider.util.conf import conf_path


def get_conf_info(path):
    """
    获取各观测对象的属性阈值
    :param path: 阈值配置文件路径
    :return: dict
    """
    result = {}

    true_path = os.path.realpath(path)
    try:
        with open(true_path, "r") as f:
            result = yaml.safe_load(f.read())
    except IOError:
        print("Anomaly Detection ERROR：Invalid config path!")

    return result

CONF_INFO = get_conf_info(conf_path)

# tcp_link信息基线
g_edges_list = {"timestamp": 0, "edges_list": {}}
EDGES_LIST_UPDATE_INTERVAL = 60 * 60

# 异常检测模型信息
class ANOMALY_DETECTION_MODEL_TYPE:
    THRESHOLD_MODEL = "1"
