#ifndef __PROBE_H__
#define __PROBE_H__

#include <stdint.h>
#include <pthread.h>

#include "fifo.h"


#define MAX_PROBE_FIFO_SIZE 1024

#define MAX_PROBE_NAME_LEN 256
#define MAX_META_PATH_LEN 4096
#define MAX_THREAD_NAME 128

#define MAX_PROBES_LIST_SIZE 2048


typedef int (*ProbeMain)();

typedef struct {
    char name[MAX_PROBE_NAME_LEN];       // key
    char metaPath[MAX_META_PATH_LEN];

    Fifo *fifo;
    ProbeMain func;

    pthread_t tid;
} Probe;

typedef struct {
    uint32_t size;
    uint32_t probesNum;
    Probe **probes;
} ProbeMgr;



Probe *ProbeCreate();
void ProbeDestroy(Probe *probe);

ProbeMgr *ProbeMgrCreate(uint32_t size);
void ProbeMgrDestroy(ProbeMgr *mgr);

int ProbeMgrPut(ProbeMgr *mgr, Probe *probe);
Probe *ProbeMgrGet(ProbeMgr *mgr, const char *probeName);

int ProbeMgrLoadProbes(ProbeMgr *mgr);

extern __thread Probe *g_probe;

#endif

