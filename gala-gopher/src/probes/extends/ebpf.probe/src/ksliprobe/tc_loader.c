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
 * Author: wo_cow
 * Create: 2022-5-16
 * Description: load tc ingress bpf
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <errno.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "ksliprobe.h"

static char g_cmdBuf[MAX_CMD_LEN];

static struct TcCmd g_enableSeq[] = {
    {
        .cmdStr = "tc qdisc del dev %s clsact >/dev/null 2>&1",
        .verifyRet = false,
    },
    {
        .cmdStr = "tc qdisc add dev %s clsact",
        .verifyRet = true,
    },
    {
        .cmdStr = "tc filter add dev %s ingress bpf direct-action obj " TC_PROG " sec tc >/dev/null 2>&1",
        .verifyRet = true,
    }
};

static int excute_cmd(const char *format, const char *ethdev)
{
    int ret;
    ret = snprintf(g_cmdBuf, MAX_CMD_LEN, format, ethdev);
    if (ret < 0) {
        return SLI_ERR;
    }

    ret = system(g_cmdBuf);
    if (ret < 0) {
        fprintf(stderr, "execute cmd[%s] error: %d\n", g_cmdBuf, ret);
        return SLI_ERR;
    }
    ret = WEXITSTATUS(ret);
    if (ret != 0) {
        return SLI_ERR;
    }
    return SLI_OK;
}

static bool netcard_enabled_other_tc(const char *ethdev)
{
    const char *format = "tc filter ls dev %s ingress | grep filter >/dev/null 2>&1";
    if (excute_cmd(format, ethdev) == SLI_OK) {
        fprintf(stderr, "%s has already enabled other tc ingress bpf\n", ethdev);
        return true;
    }

    return false;
}

static bool netcard_enabled_tc_tstamp(const char *ethdev)
{
    const char *format = "tc filter ls dev %s ingress | grep tc_tstamp.bpf.o >/dev/null 2>&1";
    if (excute_cmd(format, ethdev) == SLI_OK) {
        return true;
    }

    return false;
}


static int disable_one_netcard(const char *ethdev)
{
    if (!netcard_enabled_tc_tstamp(ethdev)) {
        return SLI_OK;
    }

    const char *format = "tc filter del dev %s ingress >/dev/null 2>&1";
    if (excute_cmd(format, ethdev) != SLI_OK) {
        DEBUG("offload netcard[%s] tc_tstamp.bpf.o err\n", ethdev);
        return SLI_ERR;
    }
    
    printf("offload netcard[%s] tc_tstamp.bpf.o success\n", ethdev);
    return SLI_OK;
}

static int enable_one_netcard(const char *ethdev)
{
    unsigned long i;
    int ret;

    if (netcard_enabled_tc_tstamp(ethdev)) {
        printf("netcard[%s] has already enabled tc_tstamp.bpf.o\n", ethdev);
        return SLI_OK;
    }

    if (netcard_enabled_other_tc(ethdev)) {
        return SLI_ERR;
    }

    for (i = 0; i < sizeof(g_enableSeq) / sizeof(struct TcCmd); i++) {
        ret = snprintf(g_cmdBuf, MAX_CMD_LEN, g_enableSeq[i].cmdStr, ethdev);
        if (ret < 0 || g_cmdBuf[MAX_CMD_LEN - 1] != '\0') {
            DEBUG("Invalid net device: %s\n", ethdev);
            return SLI_ERR;
        }

        ret = system(g_cmdBuf);
        if (ret < 0) {
            DEBUG("netcard[%s] execute cmd[%s] error: %d\n", ethdev, g_cmdBuf, ret);
            goto clear;
        }

        ret = WEXITSTATUS(ret);
        if (ret && g_enableSeq[i].verifyRet) {
            DEBUG("netcard[%s] execute cmd ret wrong: %s\n", ethdev, g_enableSeq[i].cmdStr);
            goto clear;
        }
    }

    printf("load netcard[%s] tc_tstamp.bpf.o success\n", ethdev);
    return SLI_OK;

clear:
    (void)disable_one_netcard(ethdev);
    return SLI_ERR;
}

// return: true is legal, false is illegal
static bool check_card_name_legal(const char c)
{
    if ((c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '-'
        || c == '_' || c == '@') {
        return true;
    }
    return false;
}


static int one_netcard_callback(NetdevCallback fn, char buf[])
{
    char *start = NULL;
    bool legalDev = true;

    for (start = buf; *start == ' '; start++) {
        ;
    }

    // arg is dev's name which cannot contain characters other than letters, numbers, '-' or "_".
    for (int i = 0; start[i] != 0; i++) {
        if (!check_card_name_legal(start[i])) {
            fprintf(stderr, "invalid dev name: dev name cannot contain illegal char\n");
            legalDev = false;
            break;
        }
        if (i == NAME_MAX) {
            fprintf(stderr, "invalid dev name, too long\n");
            legalDev = false;
            break;
        }
    }

    if (!legalDev) {
        legalDev = true;
        return SLI_ERR;
    }

    return fn(start);
}


static void for_each_netcard(NetdevCallback fn, char netcard_list[])
{
    int ret = SLI_OK;
    char *ptr_end = NULL;
    char *ptr_start = netcard_list;
    char buf[MAX_CMD_LEN];
    FILE *fstream = NULL;

    netcard_list[MAX_PATH_LEN - 1] = 0;

    // when there are "-n" args, enable the net card specified by -n
    if (strlen(netcard_list) > 0) {
        while (ptr_start < netcard_list + MAX_PATH_LEN && *ptr_start != '\0') {
            ptr_end = strchr(ptr_start, ',');
            if (ptr_end != NULL) {
                *ptr_end = '\0';
            }
            one_netcard_callback(fn, ptr_start);
            if (ptr_end != NULL) {
                ptr_start = ptr_end + 1;
            } else {
                break;
            }
        }

        return;
    }

    // when there are no "-n" args, enable all net cards
    fstream = fopen("/proc/net/dev", "r");
    if (fstream == NULL) {
        fprintf(stderr, "fopen /proc/net/dev err\n");
        return;
    }

    while (fgets(buf, MAX_CMD_LEN, fstream) != NULL) {
        ptr_end = strchr(buf, ':');
        if (ptr_end == NULL) {
            continue;
        }

        *ptr_end = '\0';

        one_netcard_callback(fn, buf);

        if (ret != SLI_OK) {
            (void)fclose(fstream);
            return;
        }
    }

    (void)fclose(fstream);
    return;
}

void load_tc_ingress_bpf(char netcard_list[])
{
    for_each_netcard(enable_one_netcard, netcard_list);
}

void offload_tc_ingress_bpf()
{
    // when offload we want to check all net cards
    char netcard_list[] = {0};
    for_each_netcard(disable_one_netcard, netcard_list);
}
