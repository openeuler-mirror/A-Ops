#ifndef __RESOURCE_H__
#define __RESOURCE_H__

#include <stdint.h>
#include <stdio.h>

#include "base.h"
#include "config.h"
#include "probe.h"
#include "meta.h"
#include "fifo.h"

#include "kafka.h"
#include "taosdata.h"

#include "ingress.h"
#include "egress.h"

typedef struct {
    // config
    ConfigMgr *configMgr;

    // inner component
    ProbeMgr *probeMgr;
    MeasurementMgr *mmMgr;
    FifoMgr *fifoMgr;

    // outer component
    KafkaMgr *kafkaMgr;
    TaosDbMgr *taosDbMgr;

    // thread handler
    IngressMgr *ingressMgr;
    EgressMgr *egressMgr;
} ResourceMgr;

ResourceMgr *ResourceMgrCreate();
void ResourceMgrDestroy(ResourceMgr *resourceMgr);

uint32_t ResourceMgrInit(ResourceMgr *resourceMgr);
void ResourceMgrDeinit(ResourceMgr *resourceMgr);

#endif

