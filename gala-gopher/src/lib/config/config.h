#ifndef __CONFIG_H__
#define __CONFIG_H__

#include <stdint.h>
#include "base.h"

typedef enum {
    LOG_DEBUG = 0,
    LOG_INFO,
    LOG_WARNING,
    LOG_ERROR,
    LOG_FATAL
} LOG_LEVEL;

typedef struct {
    char logDirectory[MAX_LOG_DIRECTORY_LEN];
    LOG_LEVEL logLevel;
} GlobalConfig;

typedef struct {
    uint32_t interval; // useless, it's just a placeholder
} IngressConfig;

typedef struct {
    uint32_t interval;
    uint32_t timeRange;
} EgressConfig;

typedef struct {
    char broker[MAX_KAFKA_BROKER_LEN];
    char topic[MAX_KAFKA_TOPIC_LEN];
} KafkaConfig;

typedef struct {
    char name[MAX_PROBE_NAME_LEN];
    ProbeSwitch probeSwitch;
    uint32_t interval;
} ProbeConfig;

typedef struct {
    uint32_t probesNum;
    ProbeConfig *probesConfig[MAX_PROBES_NUM];
} ProbesConfig;

typedef struct {
    char name[MAX_PROBE_NAME_LEN];
    char command[MAX_EXTEND_PROBE_COMMAND_LEN];
    char param[MAX_EXTEND_PROBE_PARAM_LEN];
    ProbeSwitch probeSwitch;
} ExtendProbeConfig;

typedef struct {
    uint32_t probesNum;
    ExtendProbeConfig *probesConfig[MAX_PROBES_NUM];
} ExtendProbesConfig;

typedef struct  {
    uint32_t maxTablesNum;
    uint32_t maxRecordsNum;
    uint32_t maxMetricsNum;
} IMDBConfig;

typedef struct {
    uint16_t port;
} WebServerConfig;

typedef struct {
    GlobalConfig *globalConfig;
    IngressConfig *ingressConfig;
    EgressConfig *egressConfig;
    KafkaConfig *kafkaConfig;
    ProbesConfig *probesConfig;
    ExtendProbesConfig *extendProbesConfig;
    IMDBConfig *imdbConfig;
    WebServerConfig *webServerConfig;
} ConfigMgr;

ConfigMgr *ConfigMgrCreate();
void ConfigMgrDestroy(ConfigMgr *mgr);

int ConfigMgrLoad(ConfigMgr *mgr, const char *confPath);

#endif

