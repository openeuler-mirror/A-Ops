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
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/epoll.h>

#include "egress.h"

EgressMgr *EgressMgrCreate(void)
{
    EgressMgr *mgr;
    mgr = (EgressMgr *)malloc(sizeof(EgressMgr));
    if (mgr == NULL)
        return NULL;

    memset(mgr, 0, sizeof(EgressMgr));

    mgr->fifo = FifoCreate(MAX_FIFO_SIZE);
    if (mgr->fifo == NULL) {
        free(mgr);
        return NULL;
    }
    return mgr;
}

void EgressMgrDestroy(EgressMgr *mgr)
{
    if (mgr == NULL)
        return;

    if (mgr->fifo != NULL)
        FifoDestroy(mgr->fifo);

    free(mgr);
    return;
}

static int EgressInit(EgressMgr *mgr)
{
    struct epoll_event event;
    int ret = 0;

    mgr->epoll_fd = epoll_create(MAX_EPOLL_SIZE);
    if (mgr->epoll_fd < 0)
        return -1;

    event.events = EPOLLIN;
    event.data.ptr = mgr->fifo;

    ret = epoll_ctl(mgr->epoll_fd, EPOLL_CTL_ADD, mgr->fifo->triggerFd, &event);
    if (ret < 0) {
        printf("[EGRESS] add EPOLLIN event failed.\n");
        return -1;
    }
    printf("[EGRESS] add EGRESS FIFO trigger success.\n");

    return 0;
}

static int EgressDataProcesssInput(Fifo *fifo, const EgressMgr *mgr)
{
    // read data from fifo
    char *dataStr = NULL;
    int ret = 0;
    KafkaMgr *kafkaMgr = mgr->kafkaMgr;

    uint64_t val = 0;
    ret = read(fifo->triggerFd, &val, sizeof(val));
    if (ret < 0) {
        ERROR("[EGRESS] Read event from triggerfd failed.\n");
        return -1;
    }

    while (FifoGet(fifo, (void **)&dataStr) == 0) {
        // Add Egress data handlement.

        if (kafkaMgr != NULL) {
            KafkaMsgProduce(kafkaMgr, dataStr, strlen(dataStr));
            DEBUG("[EGRESS] kafka produce one data: %s\n", dataStr);
        }
    }

    return 0;
}

static int EgressDataProcess(const EgressMgr *mgr)
{
    struct epoll_event events[MAX_EPOLL_EVENTS_NUM];
    int events_num;
    Fifo *fifo = NULL;
    uint32_t ret = 0;

    events_num = epoll_wait(mgr->epoll_fd, events, MAX_EPOLL_EVENTS_NUM, -1);
    if ((events_num < 0) && (errno != EINTR)) {
        ERROR("Egress Msg wait failed: %s.\n", strerror(errno));
        return events_num;
    }

    for (int i = 0; ((i < events_num) && (i < MAX_EPOLL_EVENTS_NUM)); i++) {
        if (events[i].events != EPOLLIN)
            continue;

        fifo = (Fifo *)events[i].data.ptr;
        if (fifo == NULL)
            continue;

        ret = EgressDataProcesssInput(fifo, mgr);
        if (ret != 0)
            return -1;
    }
    return 0;
}

void EgressMain(EgressMgr *mgr)
{
    int ret = 0;
    ret = EgressInit(mgr);
    if (ret != 0) {
        ERROR("[EGRESS] egress init failed.\n");
        return;
    }
    DEBUG("[EGRESS] egress init success.\n");

    for (;;) {
        ret = EgressDataProcess(mgr);
        if (ret != 0) {
            ERROR("[EGRESS] egress data process failed.\n");
            return;
        }
    }
}
