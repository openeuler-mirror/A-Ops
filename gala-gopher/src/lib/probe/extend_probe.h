#ifndef __EXTEND_PROBE_H__
#define __EXTEND_PROBE_H__

#include <stdint.h>
#include <pthread.h>

#include "base.h"
#include "fifo.h"

typedef struct {
    char name[MAX_PROBE_NAME_LEN];

    char executeCommand[MAX_EXTEND_PROBE_COMMAND_LEN];
    char executeParam[MAX_EXTEND_PROBE_PARAM_LEN];

    ProbeSwitch probeSwitch;
    Fifo *fifo;
    pthread_t tid;
} ExtendProbe;

typedef struct {
    uint32_t size;
    uint32_t probesNum;
    ExtendProbe **probes;
} ExtendProbeMgr;

ExtendProbe *ExtendProbeCreate();
void ExtendProbeDestroy(ExtendProbe *probe);
int RunExtendProbe(ExtendProbe *probe);

ExtendProbeMgr *ExtendProbeMgrCreate(uint32_t size);
void ExtendProbeMgrDestroy(ExtendProbeMgr *mgr);

int ExtendProbeMgrPut(ExtendProbeMgr *mgr, ExtendProbe *probe);
ExtendProbe *ExtendProbeMgrGet(ExtendProbeMgr *mgr, const char *probeName);


#endif

