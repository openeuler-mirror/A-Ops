#ifndef __RESOURCE_H__
#define __RESOURCE_H__

#include <stdint.h>
#include <stdio.h>

#include "base.h"
#include "config.h"
#include "imdb.h"

#include "probe.h"
#include "extend_probe.h"
#include "meta.h"
#include "fifo.h"

#include "kafka.h"

#include "ingress.h"
#include "egress.h"

#include "web_server.h"

typedef struct {
    // config
    ConfigMgr *configMgr;

    // in-memory database
    IMDB_DataBaseMgr *imdbMgr;

    // inner component
    ProbeMgr *probeMgr;
    ExtendProbeMgr *extendProbeMgr;

    MeasurementMgr *mmMgr;
    FifoMgr *fifoMgr;

    // outer component
    KafkaMgr *kafkaMgr;

    // thread handler
    IngressMgr *ingressMgr;
    EgressMgr *egressMgr;

    // web server
    WebServer *webServer;
} ResourceMgr;

ResourceMgr *ResourceMgrCreate();
void ResourceMgrDestroy(ResourceMgr *resourceMgr);

int ResourceMgrInit(ResourceMgr *resourceMgr);
void ResourceMgrDeinit(ResourceMgr *resourceMgr);

#endif

