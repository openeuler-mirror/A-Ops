#include <sys/epoll.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include "ingress.h"

IngressMgr *IngressMgrCreate()
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
    ProbeMgr *probeMgr = probeMgr = mgr->probeMgr;
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

static int IngressDataProcesssInput(Fifo *fifo, IngressMgr *mgr)
{
    // read data from fifo
    char *dataStr = NULL;
    int ret = 0;

    uint64_t val = 0;
    ret = read(fifo->triggerFd, &val, sizeof(val));
    if (ret < 0) {
        printf("[INGRESS] Read event from triggerfd failed.\n");
        return -1;
    }

    while (FifoGet(fifo, (void **)&dataStr) == 0) {

        // skip string not start with '|'
        if(strncmp(dataStr, "|", 1) != 0) {
            printf("[INGRESS] Get dirty data str: %s", dataStr);
            continue;
        }

        printf("[INGRESS] Get data str: %s", dataStr);
        // save data to imdb
        ret = IMDB_DataBaseMgrAddRecord(mgr->imdbMgr, dataStr, strlen(dataStr));
        if (ret != 0) {
            printf("[INGRESS] insert data into imdb failed.\n");
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

    // printf("[INGRESS] Get epoll event.\n");
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

