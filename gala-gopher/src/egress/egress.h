#ifndef __EGRESS__
#define __EGRESS__

#include <stdint.h>
#include <pthread.h>

#include "taosdata.h"
#include "kafka.h"

typedef struct {
    MeasurementMgr *mmMgr;
    TaosDbMgr *taosDbMgr;
    KafkaMgr *kafkaMgr;

    pthread_t tid;
} EgressMgr;


EgressMgr *EgressMgrCreate();
void EgressMgrDestroy(EgressMgr *mgr);

void EgressMain(EgressMgr *mgr);

#endif

