/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * iSulad licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Hubble_Zhu
 * Create: 2021-04-12
 * Description:
 ******************************************************************************/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "base.h"
#include "config.h"
#include "args.h"
#include "resource.h"

#if GALA_GOPHER_INFO("inner func")
static int ConfigMgrInit(ResourceMgr *resourceMgr);
static void ConfigMgrDeinit(ResourceMgr *resourceMgr);
static int ProbeMgrInit(ResourceMgr *resourceMgr);
static void ProbeMgrDeinit(ResourceMgr *resourceMgr);
static int ExtendProbeMgrInit(ResourceMgr *resourceMgr);
static void ExtendProbeMgrDeinit(ResourceMgr *resourceMgr);
static int MeasurementMgrInit(ResourceMgr *resourceMgr);
static void MeasurementMgrDeinit(ResourceMgr *resourceMgr);
static int FifoMgrInit(ResourceMgr *resourceMgr);
static void FifoMgrDeinit(ResourceMgr *resourceMgr);
static int KafkaMgrInit(ResourceMgr *resourceMgr);
static void KafkaMgrDeinit(ResourceMgr *resourceMgr);
static int IMDBMgrInit(ResourceMgr *resourceMgr);
static void IMDBMgrDeinit(ResourceMgr *resourceMgr);
static int IngressMgrInit(ResourceMgr *resourceMgr);
static void IngressMgrDeinit(ResourceMgr *resourceMgr);
static int EgressMgrInit(ResourceMgr *resourceMgr);
static void EgressMgrDeinit(ResourceMgr *resourceMgr);
static int WebServerInit(ResourceMgr *resourceMgr);
static void WebServerDeinit(ResourceMgr *resourceMgr);
#endif

typedef struct tagSubModuleInitor {
    int (*subModuleInitFunc)(ResourceMgr *);
    void (*subModuleDeinitFunc)(ResourceMgr *);
} SubModuleInitor;

extern char* g_galaConfPath;

SubModuleInitor gSubModuleInitorTbl[] = {
    { ConfigMgrInit,        ConfigMgrDeinit },      // config must be the first
    { ProbeMgrInit,         ProbeMgrDeinit },
    { ExtendProbeMgrInit,   ExtendProbeMgrDeinit },
    { MeasurementMgrInit,   MeasurementMgrDeinit },
    { FifoMgrInit,          FifoMgrDeinit },
    { KafkaMgrInit,         KafkaMgrDeinit },       // kafka must precede egress
    { IMDBMgrInit,          IMDBMgrDeinit },        // IMDB must precede ingress
    { EgressMgrInit,        EgressMgrDeinit },      // egress must precede ingress
    { IngressMgrInit,       IngressMgrDeinit },
    { WebServerInit,        WebServerDeinit }
};

ResourceMgr *ResourceMgrCreate(void)
{
    ResourceMgr *mgr = NULL;
    mgr = (ResourceMgr *)malloc(sizeof(ResourceMgr));
    if (mgr == NULL)
        return NULL;
    memset(mgr, 0, sizeof(ResourceMgr));
    return mgr;
}

void ResourceMgrDestroy(ResourceMgr *resourceMgr)
{
    if (resourceMgr != NULL)
        free(resourceMgr);

    if (g_galaConfPath != NULL) {
        free(g_galaConfPath);
        g_galaConfPath = NULL;
    }
    return;
}

int ResourceMgrInit(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL)
        return -1;

    int ret = 0;
    uint32_t initTblSize = sizeof(gSubModuleInitorTbl) / sizeof(gSubModuleInitorTbl[0]);
    for (int i = 0; i < initTblSize; i++) {
        ret = gSubModuleInitorTbl[i].subModuleInitFunc(resourceMgr);
        if (ret != 0)
            return -1;
    }

    return 0;
}

static void ResourceMgrDeleteTimer(ResourceMgr *mgr)
{
    struct itimerspec its;

    if (mgr->keeplive_timer == 0)
        return;

    (void)memset(&its, 0, sizeof(its));

    (void)timer_settime(mgr->keeplive_timer, 0, &its, NULL);

    (void)timer_delete(mgr->keeplive_timer);
    mgr->keeplive_timer = 0;
}

void ResourceMgrDeinit(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL)
        return;

    ResourceMgrDeleteTimer(resourceMgr);

    uint32_t initTblSize = sizeof(gSubModuleInitorTbl) / sizeof(gSubModuleInitorTbl[0]);
    for (int i = 0; i < initTblSize; i++)
        gSubModuleInitorTbl[i].subModuleDeinitFunc(resourceMgr);

    return;
}

#if GALA_GOPHER_INFO("inner func")
static int ConfigMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ConfigMgr *configMgr = NULL;

    configMgr = ConfigMgrCreate();
    if (configMgr == NULL) {
        ERROR("[RESOURCE] create config mgr failed.\n");
        return -1;
    }

    ret = ConfigMgrLoad(configMgr, g_galaConfPath);
    if (ret != 0) {
        ConfigMgrDestroy(configMgr);
        ERROR("[RESOURCE] load gala configuration failed.\n");
        return -1;
    }

    resourceMgr->configMgr = configMgr;
    return 0;
}

static void ConfigMgrDeinit(ResourceMgr *resourceMgr)
{
    ConfigMgrDestroy(resourceMgr->configMgr);
    resourceMgr->configMgr = NULL;
    return;
}

static int ProbeMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ConfigMgr *configMgr = NULL;
    ProbeMgr *probeMgr = NULL;

    probeMgr = ProbeMgrCreate(MAX_PROBES_NUM);
    if (probeMgr == NULL) {
        ERROR("[RESOURCE] create probe mgr failed.\n");
        return -1;
    }

    // 1. load probes
    ret = ProbeMgrLoadProbes(probeMgr);
    if (ret != 0) {
        ProbeMgrDestroy(probeMgr);
        ERROR("[RESOURCE] load probes failed.\n");
        return -1;
    }
    INFO("[RESOURCE] load probes info success.\n");

    // 2. refresh probe configuration
    configMgr = resourceMgr->configMgr;
    for (int i = 0; i < configMgr->probesConfig->probesNum; i++) {
        ProbeConfig *_probeConfig = configMgr->probesConfig->probesConfig[i];
        Probe *probe = ProbeMgrGet(probeMgr, _probeConfig->name);
        if (probe == NULL)
            continue;

        // refresh probe configuration
        probe->probeSwitch = _probeConfig->probeSwitch;
        ret = params_parse(_probeConfig->param, &probe->params);
        if (ret != 0) {
            ERROR("[RESOURCE] probes(%s) params(%s) invalid.\n", probe->name, _probeConfig->param);
        }
    }
    INFO("[RESOURCE] refresh probes configuration success.\n");

    resourceMgr->probeMgr = probeMgr;
    return 0;
}

static void ProbeMgrDeinit(ResourceMgr *resourceMgr)
{
    ProbeMgrDestroy(resourceMgr->probeMgr);
    resourceMgr->probeMgr = NULL;
    return;
}

static int ExtendProbeMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ConfigMgr *configMgr = resourceMgr->configMgr;
    ExtendProbeMgr *extendProbeMgr = NULL;

    extendProbeMgr = ExtendProbeMgrCreate(MAX_EXTEND_PROBES_NUM);
    if (extendProbeMgr == NULL) {
        ERROR("[RESOURCE] create extend probe mgr failed. \n");
        return -1;
    }

    for (int i = 0; i < configMgr->extendProbesConfig->probesNum; i++) {
        ExtendProbeConfig *_extendProbeConfig = configMgr->extendProbesConfig->probesConfig[i];
        ExtendProbe *_extendProbe = ExtendProbeCreate();
        if (_extendProbe == NULL) {
            ERROR("[RESOURCE] create extend probe failed. \n");
            return -1;
        }

        (void)strncpy(_extendProbe->name, _extendProbeConfig->name, MAX_PROBE_NAME_LEN - 1);
        (void)strncpy(_extendProbe->executeCommand, _extendProbeConfig->command, MAX_EXTEND_PROBE_COMMAND_LEN - 1);
        (void)strncpy(_extendProbe->executeParam, _extendProbeConfig->param, MAX_PARAM_LEN - 1);
        (void)strncpy(_extendProbe->startChkCmd, _extendProbeConfig->startChkCmd, MAX_EXTEND_PROBE_COMMAND_LEN - 1);

        _extendProbe->probeSwitch = _extendProbeConfig->probeSwitch;
        _extendProbe->chkType = _extendProbeConfig->startChkType;

        ret = ExtendProbeMgrPut(extendProbeMgr, _extendProbe);
        if (ret != 0) {
            ERROR("[RESOURCE] Add extend probe into extend probe mgr failed. \n");
            return -1;
        }
    }
    INFO("[RESOURCE] load extend probes success.\n");
    resourceMgr->extendProbeMgr = extendProbeMgr;
    return 0;
}

static void ExtendProbeMgrDeinit(ResourceMgr *resourceMgr)
{
    ExtendProbeMgrDestroy(resourceMgr->extendProbeMgr);
    resourceMgr->probeMgr = NULL;
    return;
}

static int MeasurementMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ProbeMgr *probeMgr = NULL;
    MeasurementMgr *mmMgr = NULL;

    mmMgr = MeasurementMgrCreate(resourceMgr->configMgr->imdbConfig->maxTablesNum, 
                                    resourceMgr->configMgr->imdbConfig->maxMetricsNum);
    if (mmMgr == NULL) {
        ERROR("[RESOURCE] create mmMgr failed.\n");
        return -1;
    }

    // load table meta info
    ret = MeasurementMgrLoad(mmMgr, GALA_META_DIR_PATH);
    if (ret != 0) {
        MeasurementMgrDestroy(mmMgr);
        ERROR("[RESOURCE] load meta dir failed.\n");
        return -1;
    }
    INFO("[RESOURCE] load meta directory success.\n");

    resourceMgr->mmMgr = mmMgr;
    return 0;
}

static void MeasurementMgrDeinit(ResourceMgr *resourceMgr)
{
    MeasurementMgrDestroy(resourceMgr->mmMgr);
    resourceMgr->mmMgr = NULL;
    return;
}

static int FifoMgrInit(ResourceMgr *resourceMgr)
{
    FifoMgr *fifoMgr = NULL;

    fifoMgr = FifoMgrCreate(MAX_FIFO_NUM);
    if (fifoMgr == NULL) {
        ERROR("[RESOURCE] create fifoMgr failed.\n");
        return -1;
    }

    resourceMgr->fifoMgr = fifoMgr;
    return 0;
}

static void FifoMgrDeinit(ResourceMgr *resourceMgr)
{
    FifoMgrDestroy(resourceMgr->fifoMgr);
    resourceMgr->fifoMgr = NULL;
    return;
}

static int KafkaMgrInit(ResourceMgr *resourceMgr)
{
    ConfigMgr *configMgr = NULL;
    KafkaMgr *kafkaMgr = NULL;

    configMgr = resourceMgr->configMgr;

    /* init metric_kafka */
    if (configMgr->kafkaConfig->kafkaSwitch == KAFKA_SWITCH_OFF) {
        ERROR("[RESOURCE] kafka switch off, skip kafkaMgr(topic:kafka_topic) create.\n");
    } else {
        kafkaMgr = KafkaMgrCreate(configMgr, "kafka_topic");
        if (kafkaMgr == NULL) {
            ERROR("[RESOURCE] create kafkaMgr(topic:kafka_topic) failed.\n");
            return -1;
        }
        resourceMgr->metric_kafkaMgr = kafkaMgr;
        INFO("[RESOURCE] create kafkaMgr(topic:kafka_topic) success.\n");
    }
    /* init meta_kafka */
    kafkaMgr = NULL;
    kafkaMgr = KafkaMgrCreate(configMgr, "metadata_topic");
    if (kafkaMgr == NULL) {
        ERROR("[RESOURCE] create kafkaMgr(topic:metadata_topic) failed.\n");
        return -1;
    }
    resourceMgr->meta_kafkaMgr = kafkaMgr;
    INFO("[RESOURCE] create kafkaMgr(topic:metadata_topic) success.\n");

    /* init event_kafka */
    kafkaMgr = NULL;
    kafkaMgr = KafkaMgrCreate(configMgr, "event_topic");
    if (kafkaMgr == NULL) {
        ERROR("[RESOURCE] create kafkaMgr(topic:event_topic) failed.\n");
        return -1;
    }
    resourceMgr->event_kafkaMgr = kafkaMgr;
    INFO("[RESOURCE] create kafkaMgr(topic:event_topic) success.\n");

    return 0;
}

static void KafkaMgrDeinit(ResourceMgr *resourceMgr)
{
    KafkaMgrDestroy(resourceMgr->metric_kafkaMgr);
    resourceMgr->metric_kafkaMgr = NULL;

    KafkaMgrDestroy(resourceMgr->meta_kafkaMgr);
    resourceMgr->meta_kafkaMgr = NULL;

    KafkaMgrDestroy(resourceMgr->event_kafkaMgr);
    resourceMgr->event_kafkaMgr = NULL;

    return;
}

static int IMDBMgrTableLoad(IMDB_Table *table, Measurement *mm)
{
    int ret = 0;
    IMDB_Record *meta = IMDB_RecordCreate(mm->fieldsNum);
    if (meta == NULL) {
        return -1;
    }

    IMDB_Metric *metric = NULL;
    uint32_t keyNum = 0;
    for (int i = 0; i < mm->fieldsNum; i++) {
        metric = IMDB_MetricCreate(mm->fields[i].name, mm->fields[i].description, mm->fields[i].type);
        if (metric == NULL) {
            goto ERR;
        }

        ret = IMDB_RecordAddMetric(meta, metric);
        if (ret != 0) {
            goto ERR;
        }

        metric = NULL;
        if (strcmp(mm->fields[i].type, METRIC_TYPE_KEY) == 0) {
            keyNum++;
        }
    }

    ret = IMDB_TableSetMeta(table, meta);
    if (ret != 0) {
        goto ERR;
    }

    ret = IMDB_TableSetRecordKeySize(table, keyNum);
    if (ret != 0) {
        goto ERR;
    }

    IMDB_TableSetEntityName(table, mm->entity);

    return 0;
ERR:
    IMDB_RecordDestroy(meta);
    IMDB_MetricDestroy(metric);
    return -1;
}

static int IMDBMgrDatabaseLoad(IMDB_DataBaseMgr *imdbMgr, MeasurementMgr *mmMgr, uint32_t recordsCapability)
{
    int ret = 0;

    IMDB_Table *table;
    for (int i = 0; i < mmMgr->measurementsNum; i++) {
        table = IMDB_TableCreate(mmMgr->measurements[i]->name, recordsCapability);
        if (table == NULL)
            return -1;

        ret = IMDBMgrTableLoad(table, mmMgr->measurements[i]);
        if (ret != 0)
            return -1;

        ret = IMDB_DataBaseMgrAddTable(imdbMgr, table);
        if (ret != 0)
            return -1;
    }

    return 0;
}

static int IMDBMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ConfigMgr *configMgr = resourceMgr->configMgr;
    IMDB_DataBaseMgr *imdbMgr = NULL;
    imdbMgr = IMDB_DataBaseMgrCreate(configMgr->imdbConfig->maxTablesNum);
    if (imdbMgr == NULL) {
        ERROR("[RESOURCE] create IMDB database mgr failed.\n");
        return -1;
    }

    IMDB_DataBaseMgrSetRecordTimeout(configMgr->imdbConfig->recordTimeout);

    ret = IMDBMgrDatabaseLoad(imdbMgr, resourceMgr->mmMgr, configMgr->imdbConfig->maxRecordsNum);
    if (ret != 0) {
        IMDB_DataBaseMgrDestroy(imdbMgr);
        return -1;
    }

    resourceMgr->imdbMgr = imdbMgr;
    return 0;
}

static void IMDBMgrDeinit(ResourceMgr *resourceMgr)
{
    IMDB_DataBaseMgrDestroy(resourceMgr->imdbMgr);
    resourceMgr->imdbMgr = NULL;
    return;
}

static int IngressMgrInit(ResourceMgr *resourceMgr)
{
    IngressMgr *ingressMgr = NULL;

    ingressMgr = IngressMgrCreate();
    if (ingressMgr == NULL) {
        ERROR("[RESOURCE] create ingressMgr failed.\n");
        return -1;
    }

    ingressMgr->fifoMgr = resourceMgr->fifoMgr;
    ingressMgr->mmMgr = resourceMgr->mmMgr;
    ingressMgr->probeMgr = resourceMgr->probeMgr;
    ingressMgr->extendProbeMgr = resourceMgr->extendProbeMgr;
    ingressMgr->imdbMgr = resourceMgr->imdbMgr;

    ingressMgr->egressMgr = resourceMgr->egressMgr;

    resourceMgr->ingressMgr = ingressMgr;
    return 0;
}

static void IngressMgrDeinit(ResourceMgr *resourceMgr)
{
    IngressMgrDestroy(resourceMgr->ingressMgr);
    resourceMgr->ingressMgr = NULL;
    return;
}

static int EgressMgrInit(ResourceMgr *resourceMgr)
{
    EgressMgr *egressMgr = NULL;

    egressMgr = EgressMgrCreate();
    if (egressMgr == NULL) {
        ERROR("[RESOURCE] create egressMgr failed.\n");
        return -1;
    }

    egressMgr->metric_kafkaMgr = resourceMgr->metric_kafkaMgr;
    egressMgr->event_kafkaMgr = resourceMgr->event_kafkaMgr;
    egressMgr->interval = resourceMgr->configMgr->egressConfig->interval;
    egressMgr->timeRange = resourceMgr->configMgr->egressConfig->timeRange;

    resourceMgr->egressMgr = egressMgr;
    return 0;
}

static void EgressMgrDeinit(ResourceMgr *resourceMgr)
{
    EgressMgrDestroy(resourceMgr->egressMgr);
    resourceMgr->egressMgr = NULL;
    return;
}

static int WebServerInit(ResourceMgr *resourceMgr)
{
    ConfigMgr *configMgr = resourceMgr->configMgr;
    WebServer *webServer = NULL;

    if (configMgr->webServerConfig->on == 0) {
        return 0;
    }
    webServer = WebServerCreate(configMgr->webServerConfig->port);
    if (webServer == NULL) {
        ERROR("[RESOURCE] create webServer failed.\n");
        return -1;
    }

    webServer->imdbMgr = resourceMgr->imdbMgr;
    resourceMgr->webServer = webServer;
    if (resourceMgr->imdbMgr)
        resourceMgr->imdbMgr->webServerOn = 1;
    return 0;
}

static void WebServerDeinit(ResourceMgr *resourceMgr)
{
    WebServerDestroy(resourceMgr->webServer);
    resourceMgr->webServer = NULL;
    return;
}

#endif

#if GALA_GOPHER_INFO("report_meta_to_kafka func")
static int metadata_build_timestamp(char *json_str, int max_len)
{
    char *str = json_str;
    int str_len = max_len;
    time_t now;
    const char *fmt = "{\"timestamp\": %lld";    // "timestamp": 1655211859000

    (void)time(&now);
    if (__snprintf(&str, str_len, &str_len, fmt, now * THOUSAND) < 0) {
        return -1;
    }
    return max_len > str_len ? (max_len - str_len) : -1;
}

static int metadata_build_metaname(const Measurement *mm, char *json_str, int max_len)
{
    char *str = json_str;
    int str_len = max_len;
    const char *fmt = ", \"meta_name\": \"%s\""; // "meta_name": "block",

    if (__snprintf(&str, str_len, &str_len, fmt, mm->name) < 0) {
        return -1;
    }
    return max_len > str_len ? (max_len - str_len) : -1;
}

static int metadata_build_entityname(const Measurement *mm, char *json_str, int max_len)
{
    char *str = json_str;
    int str_len = max_len;
    const char *fmt = ", \"entity_name\": \"%s\""; // "entity_name": "block",

    if (__snprintf(&str, str_len, &str_len, fmt, mm->entity) < 0) {
        return -1;
    }
    return max_len > str_len ? (max_len - str_len) : -1;
}

static int metadata_build_vrsion(const Measurement *mm, char *json_str, int max_len)
{
    char *str = json_str;
    int str_len = max_len;
    const char *fmt = ", \"version\": \"%s\""; // "version": "1.0.0",

    if (__snprintf(&str, str_len, &str_len, fmt, mm->version) < 0) {
        return -1;
    }
    return max_len > str_len ? (max_len - str_len) : -1;
}

/* "keys": ["machine_id", "tgid"] */
#define META_FIELD_TYPE_KEY "key"
static int metadata_build_keys(const Measurement *mm, char *json_str, int max_len)
{
    int i, ret;
    char *str = json_str;
    int str_len = max_len;
    int total_len = 0;

    ret = snprintf(str, str_len, ", \"keys\": [\"machine_id\"");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    str += ret;
    str_len -= ret;
    total_len += ret;

    for (i = 0; i < mm->fieldsNum; i++) {
        if (strcmp(mm->fields[i].type, META_FIELD_TYPE_KEY) == 0) {
            ret = snprintf(str, str_len, ", \"%s\"", mm->fields[i].name);
            if (ret < 0 || ret >= str_len) {
                return -1;
            }
            str += ret;
            str_len -= ret;
            total_len += ret;
        }
    }
    ret = snprintf(str, str_len, "]");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    total_len += ret;

    return total_len;
}

/* "labels": ["hostname", "blk_type", "comm"] */
#define META_FIELD_TYPE_LABEL "label"
static int metadata_build_labels(const Measurement *mm, char *json_str, int max_len)
{
    int i, ret;
    char *str = json_str;
    int str_len = max_len;
    int total_len = 0;

    ret = snprintf(str, str_len, ", \"labels\": [\"hostname\"");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    str += ret;
    str_len -= ret;
    total_len += ret;

    for (i = 0; i < mm->fieldsNum; i++) {
        if (strcmp(mm->fields[i].type, META_FIELD_TYPE_LABEL) == 0) {
            ret = snprintf(str, str_len, ", \"%s\"", mm->fields[i].name);
            if (ret < 0 || ret >= str_len) {
                return -1;
            }
            str += ret;
            str_len -= ret;
            total_len += ret;
        }
    }
    ret = snprintf(str, str_len, "]");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    total_len += ret;

    return total_len;
}

static int is_filed_type_metric(char *field_type)
{
    int i;

    const char meta_fileld_type_metric[][MAX_FIELD_TYPE_LEN] = {
        "counter",
        "gauge"
    };
    int size = sizeof(meta_fileld_type_metric) / sizeof(meta_fileld_type_metric[0]);

    for (i = 0; i < size; i++) {
        if (strcmp(field_type, meta_fileld_type_metric[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

/* "metrics": ["rx_bytes", "tx_bytes"] */
static int metadata_build_metrics(const Measurement *mm, char *json_str, int max_len)
{
    int i, j, ret;
    char *str = json_str;
    int str_len = max_len;
    int total_len = 0;
    int first_metric = 1;

    ret = snprintf(str, str_len, ", \"metrics\": [");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    str += ret;
    str_len -= ret;
    total_len += ret;

    for (i = 0; i < mm->fieldsNum; i++) {
        if (is_filed_type_metric((char *)mm->fields[i].type) == 0) {
            /* not metric, continue */
            continue;
        }
        if (first_metric == 1) {
            ret = snprintf(str, str_len, "\"%s\"", mm->fields[i].name);
            first_metric = 0;
        } else {
            ret = snprintf(str, str_len, ", \"%s\"", mm->fields[i].name);
        }
        if (ret < 0 || ret >= str_len) {
            return -1;
        }
        str += ret;
        str_len -= ret;
        total_len += ret;
    }

    ret = snprintf(str, str_len, "]}");
    if (ret < 0 || ret >= str_len) {
        return -1;
    }
    total_len += ret;

    return total_len;
}

static int metadata_to_json(const Measurement *mm, char *json_str, int max_json_len)
{
    int ret;
    char *str = json_str;
    int str_len = max_json_len;

    ret = metadata_build_timestamp(str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_metaname(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_entityname(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_vrsion(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_keys(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_labels(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    ret = metadata_build_metrics(mm, str, str_len);
    if (ret < 0) {
        return -1;
    }
    str += ret;
    str_len -= ret;

    return 0;
}

static int report_one_metadata(const ResourceMgr *resourceMgr, const Measurement *mm)
{
    int ret;
    char *json_str = NULL;

    KafkaMgr *meta_kafka = resourceMgr->meta_kafkaMgr;
    if (meta_kafka == NULL) {
        ERROR("[Resource] kafka topic(metadata_topic) is NULL\n");
        return -1;
    }

    json_str = (char *)malloc(MAX_DATA_STR_LEN);
    if (json_str == NULL) {
        return -1;
    }
    json_str[0] = 0;

    ret = metadata_to_json(mm, json_str, MAX_DATA_STR_LEN);
    if (ret < 0) {
        ERROR("[Resource] metadata to json failed.\n");
        goto err;
    }

    (void)KafkaMsgProduce(meta_kafka, json_str, strlen(json_str));
    DEBUG("[Resource] kafka metadata_topic produce one data: %s\n", json_str);
    return 0;

err:
    if (json_str != NULL) {
        (void)free(json_str);
    }
    return -1;
}

int ReportMeteData(const ResourceMgr *resourceMgr)
{
    MeasurementMgr *mm_mgr = NULL;
    Measurement *mm = NULL;
    int i, meta_num;

    mm_mgr = resourceMgr->mmMgr;
    if (mm_mgr == NULL) {
        ERROR("[Resource] measurement mgr is NULL\n");
        return -1;
    }
    meta_num = mm_mgr->measurementsNum;

    for (i = 0; i < meta_num; i++) {
        mm = mm_mgr->measurements[i];
        if (report_one_metadata(resourceMgr, mm) != 0) {
            ERROR("[Resource] report one metadata to kafka fail.\n");
            return -1;
        }
    }
    return 0;
}
#endif

