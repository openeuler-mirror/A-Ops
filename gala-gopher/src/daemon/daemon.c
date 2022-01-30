/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: algorithmofdish
 * Create: 2021-09-28
 * Description: provide gala-gopher daemon functions
 ******************************************************************************/
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <sys/un.h>
#include <sys/socket.h>
#include "server.h"
#include "daemon.h"

#if GALA_GOPHER_INFO("inner func declaration")
static void *DaemonRunIngress(void *arg);
static void *DaemonRunEgress(void *arg);
static void *DaemonRunSingleProbe(void *arg);
static void *DaemonRunSingleExtendProbe(void *arg);
#endif

#if GALA_GOPHER_INFO("inner func defination")
static void *DaemonRunIngress(void *arg)
{
    IngressMgr *mgr = (IngressMgr *)arg;
    prctl(PR_SET_NAME, "[INGRESS]");
    IngressMain(mgr);
}

static void *DaemonRunEgress(void *arg)
{
    EgressMgr *mgr = (EgressMgr *)arg;
    prctl(PR_SET_NAME, "[EGRESS]");
    EgressMain(mgr);
}

static void *DaemonRunSingleProbe(void *arg)
{
    g_probe = (Probe *)arg;

    char thread_name[MAX_THREAD_NAME_LEN];
    snprintf(thread_name, MAX_THREAD_NAME_LEN - 1, "[PROBE]%s", g_probe->name);
    prctl(PR_SET_NAME, thread_name);

    for (;;) {
        g_probe->func();
        sleep(g_probe->interval);
    }
}

static void *DaemonRunSingleExtendProbe(void *arg)
{
    int ret = 0;
    ExtendProbe *probe = (ExtendProbe *)arg;

    char thread_name[MAX_THREAD_NAME_LEN];
    snprintf(thread_name, MAX_THREAD_NAME_LEN - 1, "[EXTEND PROBE]%s", probe->name);
    prctl(PR_SET_NAME, thread_name);

    (void)RunExtendProbe(probe);
}

static int DaemonCheckProbeNeedStart(char *check_cmd, ProbeStartCheckType chkType)
{
    /* ret val: 1 need start / 0 no need start */
    if (!check_cmd || chkType != PROBE_CHK_CNT) {
        return 0;
    }

    int cnt = 0;
    FILE *fp = NULL;
    char data[MAX_COMMAND_LEN] = {0};
    fp = popen(check_cmd, "r");
    if (fp == NULL) {
        printf("popen error!\n");
        return 0;
    }

    if (fgets(data, sizeof(data), fp) != NULL) {
        cnt = atoi(data);
    }
    pclose(fp);

    return (cnt > 0);
}

#endif

int DaemonRun(const ResourceMgr *mgr)
{
    int ret;

    // 1. start ingress thread
    ret = pthread_create(&mgr->ingressMgr->tid, NULL, DaemonRunIngress, mgr->ingressMgr);
    if (ret != 0) {
        printf("[DAEMON] create ingress thread failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create ingress thread success.\n");

    // 2. start egress thread
    ret = pthread_create(&mgr->egressMgr->tid, NULL, DaemonRunEgress, mgr->egressMgr);
    if (ret != 0) {
        printf("[DAEMON] create egress thread failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create egress thread success.\n");

    // 3. start web_server thread
    ret = WebServerStartDaemon(mgr->webServer);
    if (ret != 0) {
        printf("[DAEMON] create web_server daemon failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create web_server daemon success.\n");

    // 4. start probe thread
    for (int i = 0; i < mgr->probeMgr->probesNum; i++) {
        Probe *_probe = mgr->probeMgr->probes[i];
        if (_probe->probeSwitch != PROBE_SWITCH_ON) {
            printf("[DAEMON] probe %s switch is off, skip create thread for it.\n", _probe->name);
            continue;
        }
        ret = pthread_create(&mgr->probeMgr->probes[i]->tid, NULL, DaemonRunSingleProbe, _probe);
        if (ret != 0) {
            printf("[DAEMON] create probe thread failed. probe name: %s errno: %d\n", _probe->name, errno);
            return -1;
        }
        printf("[DAEMON] create probe %s thread success.\n", mgr->probeMgr->probes[i]->name);
    }

    // 5. start extend probe thread
    printf("[DAEMON] start extend probe(%u) thread.\n", mgr->extendProbeMgr->probesNum);
    for (int i = 0; i < mgr->extendProbeMgr->probesNum; i++) {
        ExtendProbe *_extendProbe = mgr->extendProbeMgr->probes[i];
        if (_extendProbe->probeSwitch == PROBE_SWITCH_OFF) {
            printf("[DAEMON] extend probe %s switch is off, skip create thread for it.\n", _extendProbe->name);
            continue;
        }

        if (_extendProbe->probeSwitch == PROBE_SWITCH_AUTO) {
            ret = DaemonCheckProbeNeedStart(_extendProbe->startChkCmd, _extendProbe->chkType);
            if (ret != 1) {
                printf("[DAEMON] extend probe %s start check failed, skip create thread for it.\n", _extendProbe->name);
                continue;
            }
        }

        ret = pthread_create(&mgr->extendProbeMgr->probes[i]->tid, NULL, DaemonRunSingleExtendProbe, _extendProbe);
        if (ret != 0) {
            printf("[DAEMON] create extend probe thread failed. probe name: %s errno: %d\n", _extendProbe->name, errno);
            return -1;
        }
        printf("[DAEMON] create extend probe %s thread success.\n", mgr->extendProbeMgr->probes[i]->name);
    }

    //6. start CmdServer thread
    ret = pthread_create(&mgr->ctl_tid, NULL, CmdServer, NULL);
    if (ret != 0) {
        printf("[DAEMON] create cmd_server thread failed. errno: %d\n", errno);
        return -1;
    }
    printf("[DAEMON] create cmd_server thread success.\n");

    return 0;
}

int DaemonWaitDone(const ResourceMgr *mgr)
{
    // 1. wait ingress done
    pthread_join(mgr->ingressMgr->tid, NULL);

    // 2. wait egress done
    pthread_join(mgr->egressMgr->tid, NULL);

    // 3. wait probe done
    for (int i = 0; i < mgr->probeMgr->probesNum; i++) {
        pthread_join(mgr->probeMgr->probes[i]->tid, NULL);
    }

    // 4. wait extend probe done
    for (int i = 0; i < mgr->extendProbeMgr->probesNum; i++) {
        pthread_join(mgr->extendProbeMgr->probes[i]->tid, NULL);
    }

    // 5.wait ctl thread done
    pthread_join(mgr->ctl_tid, NULL);

    return 0;
}

