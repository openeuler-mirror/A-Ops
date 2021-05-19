#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "egress.h"

EgressMgr *EgressMgrCreate()
{
    EgressMgr *mgr;
    mgr = (EgressMgr *)malloc(sizeof(EgressMgr));
    if (mgr == NULL) {
        return NULL;
    }

    memset(mgr, 0, sizeof(EgressMgr));
    return mgr;
}

void EgressMgrDestroy(EgressMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    free(mgr);
    return;
}

static void EgressDataProcessOne(EgressMgr *mgr, const char *data)
{
    KafkaMgr *kafkaMgr = mgr->kafkaMgr;
    KafkaMsgProduce(kafkaMgr, data, strlen(data));
    printf("[EGRESS] kafka produce one data: %s\n", data);
}

static void EgressDataProcess(EgressMgr *mgr)
{
    return;
}

void EgressMain(EgressMgr *mgr)
{
    for (;;) {
        EgressDataProcess(mgr);
        sleep(mgr->interval);
    }
}

