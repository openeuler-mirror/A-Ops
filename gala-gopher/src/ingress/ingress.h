#ifndef __INGRESS_H__
#define __INGRESS_H__

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#include "base.h"
#include "fifo.h"
#include "meta.h"
#include "probe.h"
#include "extend_probe.h"
#include "imdb.h"

typedef struct {
    FifoMgr *fifoMgr;
    MeasurementMgr *mmMgr;
    ProbeMgr *probeMgr;
    ExtendProbeMgr *extendProbeMgr;

    IMDB_DataBaseMgr *imdbMgr;

    int epoll_fd;
    pthread_t tid;
} IngressMgr;

IngressMgr *IngressMgrCreate();
void IngressMgrDestroy(IngressMgr *mgr);

void IngressMain();

#endif

