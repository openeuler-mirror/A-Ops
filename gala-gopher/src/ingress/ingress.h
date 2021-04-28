#ifndef __INGRESS_H__
#define __INGRESS_H__

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#include "base.h"
#include "fifo.h"
#include "taosdata.h"
#include "meta.h"
#include "probe.h"

typedef struct {
    FifoMgr *fifoMgr;
    TaosDbMgr *taosDbMgr;
    MeasurementMgr *mmMgr;
    ProbeMgr *probeMgr;

    int epoll_fd;
    pthread_t tid;
} IngressMgr;

IngressMgr *IngressMgrCreate();
void IngressMgrDestroy(IngressMgr *mgr);

void IngressMain();

#endif

