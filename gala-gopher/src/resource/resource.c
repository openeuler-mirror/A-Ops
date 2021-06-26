#include <stdio.h>
#include <string.h>
#include <stdlib.h>
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

typedef struct tagSubModuleInitor{
    int (*subModuleInitFunc)(ResourceMgr *);
    void (*subModuleDeinitFunc)(ResourceMgr *);
} SubModuleInitor;

SubModuleInitor gSubModuleInitorTbl[] = {
    { ConfigMgrInit,        ConfigMgrDeinit },      // config must be the first
    { ProbeMgrInit,         ProbeMgrDeinit },
    { ExtendProbeMgrInit,   ExtendProbeMgrDeinit },
    { MeasurementMgrInit,   MeasurementMgrDeinit },
    { FifoMgrInit,          FifoMgrDeinit },
    // { KafkaMgrInit,         KafkaMgrDeinit },
    { IMDBMgrInit,          IMDBMgrDeinit },
    { IngressMgrInit,       IngressMgrDeinit },
    // { EgressMgrInit,        EgressMgrDeinit },
    { WebServerInit,        WebServerDeinit }
};

ResourceMgr *ResourceMgrCreate()
{
    ResourceMgr *mgr = NULL;
    mgr = (ResourceMgr *)malloc(sizeof(ResourceMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(ResourceMgr));
    return mgr;
}

void ResourceMgrDestroy(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL) {
        return;
    }
    free(resourceMgr);
    return;
}

int ResourceMgrInit(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL) {
        return -1;
    }

    int ret = 0;
    uint32_t initTblSize = sizeof(gSubModuleInitorTbl) / sizeof(gSubModuleInitorTbl[0]);
    for (int i = 0; i < initTblSize; i++) {
        ret = gSubModuleInitorTbl[i].subModuleInitFunc(resourceMgr);
        if (ret != 0) {
            return -1;
        }
    }

    return 0;
}

void ResourceMgrDeinit(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL) {
        return;
    }

    uint32_t initTblSize = sizeof(gSubModuleInitorTbl) / sizeof(gSubModuleInitorTbl[0]);
    for (int i = 0; i < initTblSize; i++) {
        gSubModuleInitorTbl[i].subModuleDeinitFunc(resourceMgr);
    }
    return;
}

#if GALA_GOPHER_INFO("inner func")
static int ConfigMgrInit(ResourceMgr *resourceMgr)
{
    int ret = 0;
    ConfigMgr *configMgr = NULL;

    configMgr = ConfigMgrCreate();
    if (configMgr == NULL) {
        printf("[RESOURCE] create config mgr failed.\n");
        return -1;
    }

    ret = ConfigMgrLoad(configMgr, GALA_CONF_PATH);
    if (ret != 0) {
        ConfigMgrDestroy(configMgr);
        printf("[RESOURCE] load gala configuration failed.\n");
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
        printf("[RESOURCE] create probe mgr failed.\n");
        return -1;
    }

    // 1. load probes
    ret = ProbeMgrLoadProbes(probeMgr);
    if (ret != 0) {
        ProbeMgrDestroy(probeMgr);
        printf("[RESOURCE] load probes failed.\n");
        return -1;
    }
    printf("[RESOURCE] load probes info success.\n");

    // 2. refresh probe configuration
    configMgr = resourceMgr->configMgr;
    for (int i = 0; i < configMgr->probesConfig->probesNum; i++) {
        ProbeConfig *_probeConfig = configMgr->probesConfig->probesConfig[i];
        Probe *probe = ProbeMgrGet(probeMgr, _probeConfig->name);
        if (probe == NULL) {
            continue;
        }

        // refresh probe configuration
        probe->interval = _probeConfig->interval;
        probe->probeSwitch = _probeConfig->probeSwitch;
    }
    printf("[RESOURCE] refresh probes configuration success.\n");

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
        printf("[RESOURCE] create extend probe mgr failed. \n");
        return -1;
    }

    for (int i = 0; i < configMgr->extendProbesConfig->probesNum; i++) {
        ExtendProbeConfig *_extendProbeConfig = configMgr->extendProbesConfig->probesConfig[i];
        ExtendProbe *_extendProbe = ExtendProbeCreate();
        if (_extendProbe == NULL) {
            printf("[RESOURCE] create extend probe failed. \n");
            return -1;
        }

        memcpy(_extendProbe->name, _extendProbeConfig->name, strlen(_extendProbeConfig->name));
        memcpy(_extendProbe->executeCommand, _extendProbeConfig->command, strlen(_extendProbeConfig->command));
        memcpy(_extendProbe->executeParam, _extendProbeConfig->param, strlen(_extendProbeConfig->param));
        memcpy(_extendProbe->startChkCmd, _extendProbeConfig->startChkCmd, strlen(_extendProbeConfig->startChkCmd));
        
        _extendProbe->probeSwitch = _extendProbeConfig->probeSwitch;
        _extendProbe->chkType = _extendProbeConfig->startChkType;

        ret = ExtendProbeMgrPut(extendProbeMgr, _extendProbe);
        if (ret != 0) {
            printf("[RESOURCE] Add extend probe into extend probe mgr failed. \n");
            return -1;
        }
    }
    printf("[RESOURCE] load extend probes success.\n");
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

    mmMgr = MeasurementMgrCreate(MAX_MEASUREMENTS_NUM);
    if (mmMgr == NULL) {
        printf("[RESOURCE] create mmMgr failed.\n");
        return -1;
    }

    // load table meta info
    ret = MeasurementMgrLoad(mmMgr, GALA_META_DIR_PATH);
    if (ret != 0) {
        MeasurementMgrDestroy(mmMgr);
        printf("[RESOURCE] load meta dir failed.\n");
        return -1;
    }
    printf("[RESOURCE] load meta directory success.\n");

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
        printf("[RESOURCE] create fifoMgr failed.\n");
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
    kafkaMgr = KafkaMgrCreate(configMgr->kafkaConfig->broker, configMgr->kafkaConfig->topic);
    if (kafkaMgr == NULL) {
        printf("[RESOURCE] create kafkaMgr failed.\n");
        return -1;
    }

    resourceMgr->kafkaMgr = kafkaMgr;
    return 0;
}

static void KafkaMgrDeinit(ResourceMgr *resourceMgr)
{
    KafkaMgrDestroy(resourceMgr->kafkaMgr);
    resourceMgr->kafkaMgr = NULL;
    return;
}

static int IMDBMgrTableLoad(IMDB_Table *table, Measurement *mm)
{
    int ret = 0;
    IMDB_Record *meta = IMDB_RecordCreate(MAX_IMDB_RECORD_CAPACITY);
    if (meta == NULL) {
        return -1;
    }

    IMDB_Metric *metric;
    for (int i = 0; i < mm->fieldsNum; i++) {
        metric = IMDB_MetricCreate(mm->fields[i].name, mm->fields[i].description, mm->fields[i].type);
        if (metric == NULL) {
            goto ERR;
        }

        ret = IMDB_RecordAddMetric(meta, metric);
        if (ret != 0) {
            goto ERR;
        }
    }

    ret = IMDB_TableSetMeta(table, meta);
    if (ret != 0) {
        goto ERR;
    }

    return 0;
ERR:
    IMDB_RecordDestroy(meta);
    return -1;
}

static int IMDBMgrDatabaseLoad(IMDB_DataBaseMgr *imdbMgr, MeasurementMgr *mmMgr)
{
    int ret = 0;

    IMDB_Table *table;
    for (int i = 0; i < mmMgr->measurementsNum; i++) {
        table = IMDB_TableCreate(mmMgr->measurements[i]->name, MAX_IMDB_TABLE_CAPACITY);
        if (table == NULL) {
            return -1;
        }

        ret = IMDBMgrTableLoad(table, mmMgr->measurements[i]);
        if (ret != 0) {
            return -1;
        }

        ret = IMDB_DataBaseMgrAddTable(imdbMgr, table);
        if (ret != 0) {
            return -1;
        }
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
        printf("[RESOURCE] create IMDB database mgr failed.\n");
        return -1;
    }

    ret = IMDBMgrDatabaseLoad(imdbMgr, resourceMgr->mmMgr);
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
        printf("[RESOURCE] create ingressMgr failed.\n");
        return -1;
    }

    ingressMgr->fifoMgr = resourceMgr->fifoMgr;
    ingressMgr->mmMgr = resourceMgr->mmMgr;
    ingressMgr->probeMgr = resourceMgr->probeMgr;
    ingressMgr->extendProbeMgr = resourceMgr->extendProbeMgr;
    ingressMgr->imdbMgr = resourceMgr->imdbMgr;

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
        printf("[RESOURCE] create egressMgr failed.\n");
        return -1;
    }

    egressMgr->kafkaMgr = resourceMgr->kafkaMgr;
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
    webServer = WebServerCreate(configMgr->webServerConfig->port);
    if (webServer == NULL) {
        printf("[RESOURCE] create webServer failed.\n");
        return -1;
    }

    webServer->imdbMgr = resourceMgr->imdbMgr;
    resourceMgr->webServer = webServer;
    return 0;
}

static void WebServerDeinit(ResourceMgr *resourceMgr)
{
    WebServerDestroy(resourceMgr->webServer);
    resourceMgr->webServer = NULL;
    return;
}

#endif

