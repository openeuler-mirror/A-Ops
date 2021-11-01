#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/epoll.h>

#include "egress.h"

EgressMgr *EgressMgrCreate()
{
    EgressMgr *mgr;
    mgr = (EgressMgr *)malloc(sizeof(EgressMgr));
    if (mgr == NULL) {
        return NULL;
    }
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
    if (mgr == NULL) {
        return;
    }

    if (mgr->fifo != NULL) {
        FifoDestroy(mgr->fifo);
    }
    free(mgr);
    return;
}

static int EgressInit(EgressMgr *mgr)
{
    struct epoll_event event;
    int ret = 0;

    mgr->epoll_fd = epoll_create(MAX_EPOLL_SIZE);
    if (mgr->epoll_fd < 0) {
        return -1;
    }

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

static int EgressDataProcesssInput(Fifo *fifo, EgressMgr *mgr)
{
    // read data from fifo
    char *dataStr = NULL;
    int ret = 0;
    KafkaMgr *kafkaMgr = mgr->kafkaMgr;

    uint64_t val = 0;
    ret = read(fifo->triggerFd, &val, sizeof(val));
    if (ret < 0) {
        printf("[EGRESS] Read event from triggerfd failed.\n");
        return -1;
    }

    while (FifoGet(fifo, (void **)&dataStr) == 0) {
        // Add Egress data handlement.

        if (kafkaMgr != NULL) {
            KafkaMsgProduce(kafkaMgr, dataStr, strlen(dataStr));
            printf("[EGRESS] kafka produce one data: %s\n", dataStr);
        } else {
            printf("[EGRESS] find no avaliable egress resource, just drop input data str.\n");
        }
        free(dataStr);
    }

    return 0;
}

static int EgressDataProcess(EgressMgr *mgr)
{
    struct epoll_event events[MAX_EPOLL_EVENTS_NUM];
    int32_t events_num = 0;
    Fifo *fifo = NULL;
    uint32_t ret = 0;

    events_num = epoll_wait(mgr->epoll_fd, events, MAX_EPOLL_EVENTS_NUM, -1);
    if (events_num < 0) {
        printf("Egress Msg wait failed: %s.\n", strerror(errno));
        if (errno == EINTR)
        {
            // 调试时会收到调试信号，返回-1，忽略即可
            events_num = 0;
        }
        return events_num;
    }

    // printf("[EGRESS] Get epoll event.\n");
    for (int i = 0; i < events_num; i++) {
        fifo = (Fifo *)events[i].data.ptr;
        ret = EgressDataProcesssInput(fifo, mgr);
        if (ret != 0) {
            return -1;
        }
    }
    return 0;

}

void EgressMain(EgressMgr *mgr)
{
    int ret = 0;
    ret = EgressInit(mgr);
    if (ret != 0) {
        printf("[EGRESS] egress init failed.\n");
        return;
    }
    printf("[EGRESS] egress init success.\n");

    for (;;) {
        ret = EgressDataProcess(mgr);
        if (ret != 0) {
            printf("[EGRESS] egress data process failed.\n");
            return;
        }
    }
}

