/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * iSulad licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Hubble_Zhu
 * Create: 2021-04-12
 * Description:
 ******************************************************************************/
#include <stdint.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <stdarg.h>

#include "probe.h"

#define MACRO2STR1(MACRO) #MACRO
#define MACRO2STR2(MACRO) MACRO2STR1(MACRO)

__thread Probe *g_probe;

Probe *ProbeCreate(void)
{
    Probe *probe = NULL;
    probe = (Probe *)malloc(sizeof(Probe));
    if (probe == NULL)
        return NULL;

    memset(probe, 0, sizeof(Probe));

    probe->fifo = FifoCreate(MAX_FIFO_SIZE);
    if (probe->fifo == NULL) {
        free(probe);
        return NULL;
    }
    return probe;
}

void ProbeDestroy(Probe *probe)
{
    if (probe == NULL)
        return;

    if (probe->fifo != NULL)
        FifoDestroy(probe->fifo);

    free(probe);
    return;
}

ProbeMgr *ProbeMgrCreate(uint32_t size)
{
    ProbeMgr *mgr = NULL;
    mgr = (ProbeMgr *)malloc(sizeof(ProbeMgr));
    if (mgr == NULL)
        return NULL;

    memset(mgr, 0, sizeof(ProbeMgr));

    mgr->probes = (Probe **)malloc(sizeof(Probe *) * size);
    if (mgr->probes == NULL) {
        free(mgr);
        return NULL;
    }
    memset(mgr->probes, 0, sizeof(Probe *) * size);

    mgr->size = size;
    return mgr;
}

void ProbeMgrDestroy(ProbeMgr *mgr)
{
    if (mgr == NULL)
        return;

    if (mgr->probes != NULL) {
        for (int i = 0; i < mgr->probesNum; i++)
            ProbeDestroy(mgr->probes[i]);

        free(mgr->probes);
    }

    free(mgr);
    return;
}

int ProbeMgrPut(ProbeMgr *mgr, Probe *probe)
{
    if (mgr->probesNum == mgr->size)
        return -1;

    mgr->probes[mgr->probesNum] = probe;
    mgr->probesNum++;
    return 0;
}

Probe *ProbeMgrGet(ProbeMgr *mgr, const char *probeName)
{
    for (int i = 0; i < mgr->probesNum; i++) {
        if (strcmp(mgr->probes[i]->name, probeName) == 0)
            return mgr->probes[i];
    }
    return NULL;
}

int ProbeMgrLoadProbes(ProbeMgr *mgr)
{
    int count = 0;
    char *p = NULL;

    char probesList[] = MACRO2STR2(PROBES_LIST);
    char probesMetaList[] = MACRO2STR2(PROBES_META_LIST);

    Probe *probe;
    int ret;
    // get probe name
    count = 0;
    p = strtok(probesList, " ");
    while (p != NULL) {
        probe = ProbeCreate();
        if (probe == NULL)
            return -1;

        memcpy(probe->name, p, strlen(p));

        ret = ProbeMgrPut(mgr, probe);
        if (ret != 0)
            return 0;

        p = strtok(NULL, " ");
        count++;
    }

    // get probe meta path
    count = 0;
    p = strtok(probesMetaList, " ");
    while (p != NULL) {
        memcpy(mgr->probes[count]->metaPath, p, strlen(p));
        p = strtok(NULL, " ");
        count++;
    }

    // get probe process func
    char probeMainStr[MAX_PROBE_NAME_LEN];
    void *hdl = dlopen(NULL, RTLD_NOW | RTLD_GLOBAL);
    if (hdl == NULL)
        return -1;

    printf("[PROBE] get probes_num: %u\n", mgr->probesNum);
    for (int i = 0; i < mgr->probesNum; i++) {
        (void)snprintf(probeMainStr, MAX_PROBE_NAME_LEN - 1, "probe_main_%s", mgr->probes[i]->name);
        mgr->probes[i]->func = dlsym(hdl, (char *)probeMainStr);
        if (mgr->probes[i]->func == NULL) {
            printf("[PROBE] Unknown func: %s\n", probeMainStr);
            dlclose(hdl);
            return -1;
        }
    }

    dlclose(hdl);
    return 0;
}

int __wrap_fprintf(FILE *stream, const char *format, ...)
{
    char ch = 0;
    char *pc = NULL;
    uint32_t ret = 0;
    char *curFormat = format;
    uint32_t index = 0;
    char *dataStr = (char *)malloc(MAX_DATA_STR_LEN);
    if (dataStr == NULL)
        return -1;

    memset(dataStr, 0, MAX_DATA_STR_LEN);

    va_list arg;
    va_start(arg, curFormat);

    while (*curFormat) {
        char ret = *curFormat;
        if (ret == '%') {
            switch (*++curFormat) {
                case 'c':
                    ch = va_arg(arg, int);
                    memcpy(dataStr + index, &ch, 1);
                    index++;
                    break;
                case 's':
                    pc = va_arg(arg, char *);
                    while (*pc != 0) {
                        memcpy(dataStr + index, pc, 1);
                        index++;
                        pc++;
                    }
                    break;
                default:
                    break;
            }
        } else {
            memcpy(dataStr + index, curFormat, 1);
            index++;
        }
        curFormat++;
    }
    va_end(arg);

    ret = FifoPut(g_probe->fifo, (void *)dataStr);
    if (ret != 0) {
        DEBUG("[PROBE %s] fifo full.\n", g_probe->name);
        return -1;
    }

    uint64_t msg = 1;
    ret = write(g_probe->fifo->triggerFd, &msg, sizeof(uint64_t));
    if (ret != sizeof(uint64_t)) {
        DEBUG("[PROBE %s] send trigger msg to eventfd failed.\n", g_probe->name);
        return -1;
    }

    return 0;
}
