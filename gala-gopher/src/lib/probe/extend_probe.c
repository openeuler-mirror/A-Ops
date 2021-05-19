#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "extend_probe.h"

ExtendProbe *ExtendProbeCreate()
{
    ExtendProbe *probe = NULL;
    probe = (ExtendProbe *)malloc(sizeof(ExtendProbe));
    if (probe == NULL) {
        return NULL;
    }
    memset(probe, 0, sizeof(ExtendProbe));

    probe->fifo = FifoCreate(MAX_FIFO_SIZE);
    if (probe->fifo == NULL) {
        free(probe);
        return NULL;
    }
    return probe;
}

void ExtendProbeDestroy(ExtendProbe *probe)
{
    if (probe == NULL) {
        return;
    }

    if (probe->fifo != NULL) {
        FifoDestroy(probe->fifo);
    }
    free(probe);
    return;
}

int RunExtendProbe(ExtendProbe *probe)
{
    int ret = 0;
    FILE *f = NULL;
    char dataStr[MAX_DATA_STR_LEN];

    char command[MAX_COMMAND_LEN];
    snprintf(command, MAX_COMMAND_LEN - 1, "%s %s", probe->executeCommand, probe->executeParam);
    f = popen(command, "r");

    while (!feof(f) && !ferror(f)) {
        memset(dataStr, 0, sizeof(MAX_DATA_STR_LEN));
        fgets(dataStr, sizeof(dataStr), f);
        printf("[EXTEND PROBE %s] Get data str: %s", probe->name, dataStr);

        ret = FifoPut(probe->fifo, (void *)dataStr);
        if (ret != 0) {
            printf("[EXTEND PROBE %s] fifo full.\n", probe->name);
            fclose(f);
            return -1;
        }

        uint64_t msg = 1;
        ret = write(probe->fifo->triggerFd, &msg, sizeof(uint64_t));
        if (ret != sizeof(uint64_t)) {
            printf("[EXTEND PROBE %s] send trigger msg to eventfd failed.\n", probe->name);
            fclose(f);
            return -1;
        }
    }

    fclose(f);
    return 0;
}

ExtendProbeMgr *ExtendProbeMgrCreate(uint32_t size)
{
    ExtendProbeMgr *mgr = NULL;
    mgr = (ExtendProbeMgr *)malloc(sizeof(ExtendProbeMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(ExtendProbeMgr));

    mgr->probes = (ExtendProbe **)malloc(sizeof(ExtendProbe *) * size);
    if (mgr->probes == NULL) {
        free(mgr);
        return NULL;
    }
    memset(mgr->probes, 0, sizeof(ExtendProbe *) * size);

    mgr->size = size;
    return mgr;
}

void ExtendProbeMgrDestroy(ExtendProbeMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    if (mgr->probes != NULL) {
        for (int i = 0; i < mgr->probesNum; i++) {
            ExtendProbeDestroy(mgr->probes[i]);
        }
        free(mgr->probes);
    }
    free(mgr);
    return;
}

int ExtendProbeMgrPut(ExtendProbeMgr *mgr, ExtendProbe *probe)
{
    if (mgr->probesNum == mgr->size) {
        return -1;
    }

    mgr->probes[mgr->probesNum] = probe;
    mgr->probesNum++;
    return 0;
}

ExtendProbe *ExtendProbeMgrGet(ExtendProbeMgr *mgr, const char *probeName)
{
    for (int i = 0; i < mgr->probesNum; i++) {
        if (strcmp(mgr->probes[i]->name, probeName) == 0) {
            return mgr->probes[i];
        }
    }
    return NULL;
}

