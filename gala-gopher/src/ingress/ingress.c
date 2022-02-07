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
#include <sys/epoll.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include "ingress.h"

IngressMgr *IngressMgrCreate(void)
{
    IngressMgr *mgr = NULL;
    mgr = (IngressMgr *)malloc(sizeof(IngressMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(IngressMgr));
    return mgr;
}

void IngressMgrDestroy(IngressMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    free(mgr);
    return;
}

static int IngressInit(IngressMgr *mgr)
{
    struct epoll_event event;
    uint32_t ret = 0;

    mgr->epoll_fd = epoll_create(MAX_EPOLL_SIZE);
    if (mgr->epoll_fd < 0) {
        return -1;
    }

    // add all probe triggerFd into mgr->epoll_fd
    ProbeMgr *probeMgr = mgr->probeMgr;
    for (int i = 0; i < probeMgr->probesNum; i++) {
        Probe *probe = probeMgr->probes[i];
        event.events = EPOLLIN;
        event.data.ptr = probe->fifo;

        ret = epoll_ctl(mgr->epoll_fd, EPOLL_CTL_ADD, probe->fifo->triggerFd, &event);
        if (ret < 0) {
            printf("[INGRESS] add EPOLLIN event failed, probe %s.\n", probe->name);
            return -1;
        }

        printf("[INGRESS] Add EPOLLIN event success, probe %s.\n", probe->name);
    }

    // add all extend probe triggerfd into mgr->epoll_fd
    ExtendProbeMgr *extendProbeMgr = mgr->extendProbeMgr;
    for (int i = 0; i < extendProbeMgr->probesNum; i++) {
        ExtendProbe *extendProbe = extendProbeMgr->probes[i];
        event.events = EPOLLIN;
        event.data.ptr = extendProbe->fifo;

        ret = epoll_ctl(mgr->epoll_fd, EPOLL_CTL_ADD, extendProbe->fifo->triggerFd, &event);
        if (ret < 0) {
            printf("[INGRESS] add EPOLLIN event failed, extend probe %s.\n", extendProbe->name);
            return -1;
        }

        printf("[INGRESS] Add EPOLLIN event success, extend probe %s.\n", extendProbe->name);
    }

    return 0;
}

static int IngressData2Egress(IngressMgr *mgr, const char *dataStr, int dataStrLen)
{
    int ret = 0;

    // format data to json
    char *jsonStr = malloc(MAX_DATA_STR_LEN);
    if (jsonStr == NULL) {
        printf("[INGRESS] alloc jsonStr failed.\n");
    }
    ret = IMDB_DataStr2Json(mgr->imdbMgr, dataStr, strlen(dataStr), jsonStr, MAX_DATA_STR_LEN);
    if (ret != 0) {
        DEBUG("[INGRESS] reformat dataStr to json failed.\n");
    }
    ret = FifoPut(mgr->egressMgr->fifo, (void *)jsonStr);
    if (ret != 0) {
        DEBUG("[INGRESS] egress fifo full.\n");
        return -1;
    }

    uint64_t msg = 1;
    ret = write(mgr->egressMgr->fifo->triggerFd, &msg, sizeof(uint64_t));
    if (ret != sizeof(uint64_t)) {
        DEBUG("[INGRESS] send trigger msg to egress eventfd failed.\n");
        return -1;
    }

    return 0;
}

static int IngressDataProcesssInput(Fifo *fifo, IngressMgr *mgr)
{
    // read data from fifo
    char *dataStr = NULL;
    int ret = 0;

    uint64_t val = 0;
    ret = read(fifo->triggerFd, &val, sizeof(val));
    if (ret < 0) {
        DEBUG("[INGRESS] Read event from triggerfd failed.\n");
        return -1;
    }

    while (FifoGet(fifo, (void **)&dataStr) == 0) {
        // skip string not start with '|'
        if (strncmp(dataStr, "|", 1) != 0) {
            DEBUG("[INGRESS] Get dirty data str: %s\n", dataStr);
            continue;
        }

        // save data to imdb
        ret = IMDB_DataBaseMgrAddRecord(mgr->imdbMgr, dataStr, strlen(dataStr));
        if (ret != 0) {
            DEBUG("[INGRESS] insert data into imdb failed.\n");
        }

        // send data to egress
        ret = IngressData2Egress(mgr, dataStr, strlen(dataStr));
        if (ret != 0) {
            DEBUG("[INGRESS] send data to egress failed.\n");
        }

        free(dataStr);
    }

    return 0;
}

static int IngressDataProcesss(IngressMgr *mgr)
{
    struct epoll_event events[MAX_EPOLL_EVENTS_NUM];
    uint32_t events_num = 0;
    Fifo *fifo = NULL;
    uint32_t ret = 0;

    events_num = epoll_wait(mgr->epoll_fd, events, MAX_EPOLL_EVENTS_NUM, -1);
    if (events_num < 0) {
        return -1;
    }

    for (int i = 0; i < events_num; i++) {
        fifo = (Fifo *)events[i].data.ptr;
        ret = IngressDataProcesssInput(fifo, mgr);
        if (ret != 0) {
            return -1;
        }
    }
    return 0;
}

void IngressMain(IngressMgr *mgr)
{
    int ret = 0;
    ret = IngressInit(mgr);
    if (ret != 0) {
        printf("[INGRESS] ingress init failed.\n");
        return;
    }
    printf("[INGRESS] ingress init success.\n");

    for (;;) {
        ret = IngressDataProcesss(mgr);
        if (ret != 0) {
            printf("[INGRESS] ingress data process failed.\n");
            return;
        }
    }
}

