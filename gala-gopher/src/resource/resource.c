#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "resource.h"

#if GALA_GOPHER_INFO("inner func")
static uint32_t ConfigMgrInit(ResourceMgr *resourceMgr);
static void ConfigMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t ProbeMgrInit(ResourceMgr *resourceMgr);
static void ProbeMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t MeasurementMgrInit(ResourceMgr *resourceMgr);
static void MeasurementMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t FifoMgrInit(ResourceMgr *resourceMgr);
static void FifoMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t KafkaMgrInit(ResourceMgr *resourceMgr);
static void KafkaMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t TaosMgrInit(ResourceMgr *resourceMgr);
static void TaosMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t IngressMgrInit(ResourceMgr *resourceMgr);
static void IngressMgrDeinit(ResourceMgr *resourceMgr);
static uint32_t EgressMgrInit(ResourceMgr *resourceMgr);
static void EgressMgrDeinit(ResourceMgr *resourceMgr);
#endif

typedef struct {
    uint32_t (*subModuleInitFunc)(ResourceMgr *);
    void (*subModuleDeinitFunc)(ResourceMgr *);
} SubModuleInitor;

SubModuleInitor gSubModuleInitorTbl[] = {
    { ConfigMgrInit,        ConfigMgrDeinit },      // config must be the first
    { ProbeMgrInit,         ProbeMgrDeinit },
    { MeasurementMgrInit,   MeasurementMgrDeinit },
    { FifoMgrInit,          FifoMgrDeinit },
    { KafkaMgrInit,         KafkaMgrDeinit },
    { TaosMgrInit,          TaosMgrDeinit },
    { IngressMgrInit,       IngressMgrDeinit },
    { EgressMgrInit,        EgressMgrDeinit }
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

uint32_t ResourceMgrInit(ResourceMgr *resourceMgr)
{
    if (resourceMgr == NULL) {
        return -1;
    }

    uint32_t ret = 0;
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
static uint32_t ConfigMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
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

static uint32_t ProbeMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
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

static uint32_t MeasurementMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
    ProbeMgr *probeMgr = NULL;
    MeasurementMgr *mmMgr = NULL;
    
    mmMgr = MeasurementMgrCreate(MAX_MEASUREMENTS_NUM);
    if (mmMgr == NULL) {
        printf("[RESOURCE] create mmMgr failed.\n");
        return -1;
    }

    // load table meta info
    probeMgr = resourceMgr->probeMgr;
    for (int i = 0; i < probeMgr->probesNum; i++) {
        ret = MeasurementMgrLoad(mmMgr, probeMgr->probes[i]->metaPath);
        if (ret != 0) {
            MeasurementMgrDestroy(mmMgr);
            printf("[RESOURCE] load probe %s meta path failed.\n", probeMgr->probes[i]->name);
            return -1;
        }
    }
    printf("[RESOURCE] load probes meta path success.\n");

    resourceMgr->mmMgr = mmMgr;
    return 0;
}

static void MeasurementMgrDeinit(ResourceMgr *resourceMgr)
{
    MeasurementMgrDestroy(resourceMgr->mmMgr);
    resourceMgr->mmMgr = NULL;
    return;
}

static uint32_t FifoMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
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

static uint32_t KafkaMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
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

static uint32_t TaosMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
    ConfigMgr *configMgr = NULL;
    MeasurementMgr *mmMgr = NULL;
    TaosDbMgr *taosDbMgr = NULL;

    configMgr = resourceMgr->configMgr;
    taosDbMgr = TaosDbMgrCreate(configMgr->taosdataConfig->ip, configMgr->taosdataConfig->user,
        configMgr->taosdataConfig->pass, configMgr->taosdataConfig->dbName, configMgr->taosdataConfig->port);
    if (taosDbMgr == NULL) {
        printf("[RESOURCE] create taosDbMgr failed.\n");
        return -1;
    }

    // 1. create tables in taosdata
    mmMgr = resourceMgr->mmMgr;
    for (int i = 0; i < mmMgr->measurementsNum; i++) {
        ret = TaosDbMgrCreateTable(mmMgr->measurements[i], taosDbMgr);
        if (ret != 0) {
            printf("[DAEMON] create table %s failed.\n", mmMgr->measurements[i]->name);
            TaosDbMgrDestroy(taosDbMgr);
            return -1;
        }
        /*
        ret = TaosDbMgrSubscribeTable(mmMgr->measurements[i], taosDbMgr);
        if (ret != 0) {
            printf("[DAEMON] subscribe table %s failed.\n", mmMgr->measurements[i]->name);
            return -1;
        }
        */
    }
    printf("[DAEMON] create all measurements success.\n");

    resourceMgr->taosDbMgr = taosDbMgr;
    return 0;
}

static void TaosMgrDeinit(ResourceMgr *resourceMgr)
{
    TaosDbMgrDestroy(resourceMgr->taosDbMgr);
    resourceMgr->taosDbMgr = NULL;
    return;
}

static uint32_t IngressMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
    IngressMgr *ingressMgr = NULL;

    ingressMgr = IngressMgrCreate();
    if (ingressMgr == NULL) {
        printf("[RESOURCE] create ingressMgr failed.\n");
        return -1;
    }

    ingressMgr->fifoMgr = resourceMgr->fifoMgr;
    ingressMgr->mmMgr = resourceMgr->mmMgr;
    ingressMgr->probeMgr = resourceMgr->probeMgr;
    ingressMgr->taosDbMgr = resourceMgr->taosDbMgr;

    resourceMgr->ingressMgr = ingressMgr;
    return 0;
}

static void IngressMgrDeinit(ResourceMgr *resourceMgr)
{
    IngressMgrDestroy(resourceMgr->ingressMgr);
    resourceMgr->ingressMgr = NULL;
    return;
}

static uint32_t EgressMgrInit(ResourceMgr *resourceMgr)
{
    uint32_t ret = 0;
    EgressMgr *egressMgr = NULL;

    egressMgr = EgressMgrCreate();
    if (egressMgr == NULL) {
        printf("[RESOURCE] create egressMgr failed.\n");
        return -1;
    }

    egressMgr->mmMgr = resourceMgr->mmMgr;
    egressMgr->taosDbMgr = resourceMgr->taosDbMgr;
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

#endif

