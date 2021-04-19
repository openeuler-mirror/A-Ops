#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>

#include "daemon.h"

// configuration for taosdata
#define TAOS_IP   "localhost"
#define TAOS_USER "root"
#define TAOS_PASS "taosdata"
#define TAOS_DB   "gala_gopher"
#define TAOS_PORT 0

#define KAFKA_BROKER "localhost:9092"
#define KAFKA_TOPIC  "gala_gopher"

#define MAX_MEASUREMENTS_NUM 64
#define MAX_PROBES_NUM 64
#define MAX_FIFO_NUM MAX_PROBES_NUM


ResourceMgr *ResourceMgrCreate()
{
    ResourceMgr *mgr;
    mgr = (ResourceMgr *)malloc(sizeof(ResourceMgr));
    if (mgr == NULL) {
        return NULL;
    }

    memset(mgr, 0, sizeof(ResourceMgr));
    mgr->probeMgr = ProbeMgrCreate(MAX_PROBES_NUM);
    if (mgr->probeMgr == NULL) {
        printf("[DAEMON] create ProbeMgr failed.\n");
        goto ERR;
    }

    mgr->mmMgr = MeasurementMgrCreate(MAX_MEASUREMENTS_NUM);
    if (mgr->mmMgr == NULL) {
        printf("[DAEMON] create MeasurementMgr failed.\n");
        goto ERR;
    }

    mgr->fifoMgr = FifoMgrCreate(MAX_FIFO_NUM);
    if (mgr->fifoMgr == NULL) {
        printf("[DAEMON] create fifoMgr failed.\n");
        goto ERR;
    }

    mgr->kafkaMgr = KafkaMgrCreate(KAFKA_BROKER, KAFKA_TOPIC);
    if (mgr->kafkaMgr == NULL) {
        printf("[DAEMON] create kafkaMgr failed.\n");
        goto ERR;
    }

    mgr->taosDbMgr = TaosDbMgrCreate(TAOS_IP, TAOS_USER, TAOS_PASS, TAOS_DB, TAOS_PORT);
    if (mgr->taosDbMgr == NULL) {
        printf("[DAEMON] create taosDbMgr failed.\n");
        goto ERR;
    }

    mgr->ingressMgr = IngressMgrCreate();
    if (mgr->ingressMgr == NULL) {
        printf("[DAEMON] create ingressMgr failed.\n");
        goto ERR;
    }
    mgr->ingressMgr->fifoMgr = mgr->fifoMgr;
    mgr->ingressMgr->mmMgr = mgr->mmMgr;
    mgr->ingressMgr->probeMgr = mgr->probeMgr;
    mgr->ingressMgr->taosDbMgr = mgr->taosDbMgr;

    mgr->egressMgr = EgressMgrCreate();
    if (mgr->egressMgr == NULL) {
        printf("[DAEMON] create egressMgr failed.\n");
        goto ERR;
    }
    mgr->egressMgr->mmMgr = mgr->mmMgr;
    mgr->egressMgr->taosDbMgr = mgr->taosDbMgr;
    mgr->egressMgr->kafkaMgr = mgr->kafkaMgr;

    return mgr;
ERR:
    ResourceMgrDestroy(mgr);
    return NULL;
}

void ResourceMgrDestroy(ResourceMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    EgressMgrDestroy(mgr->egressMgr);
    IngressMgrDestroy(mgr->ingressMgr);
    TaosDbMgrDestroy(mgr->taosDbMgr);
    KafkaMgrDestroy(mgr->kafkaMgr);
    FifoMgrDestroy(mgr->fifoMgr);
    MeasurementMgrDestroy(mgr->mmMgr);
    ProbeMgrDestroy(mgr->probeMgr);

    free(mgr);
    return;
}

uint32_t DaemonInit(ResourceMgr *mgr)
{
    uint32_t ret = 0;
    // 0. load configuration

    // 1. load probes
    ret = ProbeMgrLoadProbes(mgr->probeMgr);
    if (ret != 0) {
        printf("[DAEMON] load probes failed.\n");
        return -1;
    }
    printf("[DAEMON] load probes success.\n");

    // 2. load table meta info
    for (int i = 0; i < mgr->probeMgr->probesNum; i++) {
        ret = MeasurementMgrLoad(mgr->mmMgr, mgr->probeMgr->probes[i]->metaPath);
        if (ret != 0) {
            printf("[DAEMON] load probe %s meta path failed.\n", mgr->probeMgr->probes[i]->name);
            return -1;
        }
    }
    printf("[DAEMON] load probes meta path success.\n");

    // 3. create and subscribe tables in taosdata
    for (int i = 0; i < mgr->mmMgr->measurementsNum; i++) {
        ret = TaosDbMgrCreateTable(mgr->mmMgr->measurements[i], mgr->taosDbMgr);

        if (ret != 0) {
            printf("[DAEMON] create table %s failed.\n", mgr->mmMgr->measurements[i]->name);
            return -1;
        }
        ret = TaosDbMgrSubscribeTable(mgr->mmMgr->measurements[i], mgr->taosDbMgr);
        if (ret != 0) {
            printf("[DAEMON] subscribe table %s failed.\n", mgr->mmMgr->measurements[i]->name);
            return -1;
        }
    }
    printf("[DAEMON] create and subscribe all measurements success.\n");

    return 0;
}

static void *DaemonRunIngress(void *arg)
{
    IngressMgr *mgr = (IngressMgr *)arg;
    prctl(PR_SET_NAME, "[INGRESS]");
    IngressMain(mgr);
}

static void *DaemonRunEgress(void *arg)
{
    EgressMgr *mgr = (EgressMgr *)arg;
    prctl(PR_SET_NAME, "[EGRESS]");
    EgressMain(mgr);
}

static void *DaemonRunSingleProbe(void *arg)
{
    g_probe = (Probe *)arg;

    char thread_name[MAX_THREAD_NAME];
    snprintf(thread_name, MAX_THREAD_NAME - 1, "[PROBE]%s", g_probe->name);
    prctl(PR_SET_NAME, thread_name);

    for (;;) {
        g_probe->func();
        sleep(1);
    }
    return 0;
}

uint32_t DaemonRun(ResourceMgr *mgr)
{
    uint32_t ret;

    // 1. start ingress thread
    ret = pthread_create(&mgr->ingressMgr->tid, NULL, DaemonRunIngress, mgr->ingressMgr);
    if (ret != 0) {
        printf("[DAEMON] create ingress thread failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create ingress thread success.\n", errno);
    // sleep(1);

    // 2. start egress thread
    ret = pthread_create(&mgr->egressMgr->tid, NULL, DaemonRunEgress, mgr->egressMgr);
    if (ret != 0) {
        printf("[DAEMON] create egress thread failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create egress thread success.\n", errno);
    // sleep(1);

    // 3. start probe thread
    for (int i = 0; i < mgr->probeMgr->probesNum; i++) {
        ret = pthread_create(&mgr->probeMgr->probes[i]->tid, NULL, DaemonRunSingleProbe, mgr->probeMgr->probes[i]);
        if (ret != 0) {
            printf("[DAEMON] create probe thread failed. probe name: %s errno: %d\n", mgr->probeMgr->probes[i]->name, errno);
            return -1;
        }
        printf("[DAEMON] create probe %s thread success.\n", mgr->probeMgr->probes[i]->name);
        // sleep(1);
    }

    return 0;
}

uint32_t DaemonWaitDone(ResourceMgr *mgr)
{
    // 1. wait ingress done
    pthread_join(mgr->ingressMgr->tid, NULL);
    
    // 2. wait egress done
    pthread_join(mgr->egressMgr->tid, NULL);
    
    // 3. wait probe done
    for (int i = 0; i < mgr->probeMgr->probesNum; i++) {
        pthread_join(mgr->probeMgr->probes[i]->tid, NULL);
    }

    return 0;
}

