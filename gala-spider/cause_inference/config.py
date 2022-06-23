ARANGO_URL = 'http://localhost:8529'
ARANGO_DB = 'spider'
# 异常时间点的拓扑图查询所容忍的时间偏移，单位：秒
TOLERATED_TS_BIAS = 120
CAUSAL_GRAPH_DEPTH = 10
ROOT_CAUSE_TOPK = 3
# 单位： 秒
SAMPLE_DURATION_OF_HIST_METRIC = 600

KAFKA_ABNORMAL_KPI_TOPIC = 'gala_anteater_hybrid_model'
KAFKA_ABNORMAL_METRIC_TOPIC = 'gala_anteater_metric'
KAFKA_SERVER = 'localhost:9092'
KAFKA_KPI_GROUP_ID = 'gala_anteater_kpi'
KAFKA_METRIC_GROUP_ID = 'gala_anteater_metric'
KAFKA_CONSUMER_TO = 1
KAFKA_AUTO_OFFSET_RESET = 'latest'

# 根因定位时，有效的异常指标事件周期，单位：秒
EVENT_VALID_METRIC_DURATION = 120
# 异常指标事件的老化周期，单位：秒
EVENT_AGING_METRIC_DURATION = 600
KAFKA_CAUSE_INFER_TOPIC = 'gala_cause_inference'

OBSERVE_META_PATH = '/etc/spider/observe.yaml'

# prometheus 配置
PROMETHEUS_BASE_URL = 'http://localhost:9090/'
PROMETHEUS_RANGE_API = '/api/v1/query_range'
PROMETHEUS_STEP = 5

LOG_PATH = '/var/log/gala-spider/cause-inference.log'
LOG_LEVEL = 'DEBUG'
LOG_MAX_SIZE = 10 * 1000 * 1000
LOG_BACKUP_COUNT = 10
