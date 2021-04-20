#ifndef __DAEMON_H__
#define __DAEMON_H__

#include <stdint.h>
#include <stdio.h>

#include "base.h"
#include "config.h"
#include "ingress.h"
#include "egress.h"
#include "fifo.h"

#include "meta.h"
#include "probe.h"
#include "taosdata.h"
#include "kafka.h"

typedef struct {
    MeasurementMgr *mmMgr;
    ProbeMgr *probeMgr;
    FifoMgr *fifoMgr;

    TaosDbMgr *taosDbMgr;
    KafkaMgr *kafkaMgr;

    IngressMgr *ingressMgr;
    EgressMgr *egressMgr;
} ResourceMgr;

ResourceMgr *ResourceMgrCreate(ConfigMgr *configMgr);
void ResourceMgrDestroy(ResourceMgr *mgr);

uint32_t DaemonInit(ResourceMgr *mgr, ConfigMgr *configMgr);
uint32_t DaemonRun(ResourceMgr *mgr);
uint32_t DaemonWaitDone(ResourceMgr *mgr);

#endif

