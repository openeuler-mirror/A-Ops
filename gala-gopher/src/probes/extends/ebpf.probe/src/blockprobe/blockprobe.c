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
 * Author: luzhihao
 * Create: 2022-02-22
 * Description: block probe
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "blockprobe.skel.h"
#include "blockprobe_iscsi.skel.h"
#include "blockprobe_iscsi_tp.skel.h"
#include "blockprobe_iscsi_sas.skel.h"
#include "blockprobe.h"

#define OO_NAME "block"  // Observation Object name
#define ISCSI_MOD "libiscsi"
#define ISCSI_SAS_MOD "libsas"
#define ISCSI_TP_MOD "scsi_transport_iscsi"
#define BLOCK_MAP_PATH "/sys/fs/bpf/probe/block_map"

#define __LOAD_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, block_map, BLOCK_MAP_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static volatile sig_atomic_t g_stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};

static void sig_int(int signo)
{
    g_stop = 1;
}

static char __is_exist_mod(const char *mod)
{
    int cnt = 0;
    FILE *fp;
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    cmd[0] = 0;
    (void)snprintf(cmd, COMMAND_LEN, "lsmod | grep -w %s | wc -l", mod);
    fp = popen(cmd, "r");
    if (fp == NULL) {
        return 0;
    }

    line[0] = 0;
    if (fgets(line, LINE_BUF_LEN, fp) != NULL) {
        SPLIT_NEWLINE_SYMBOL(line);
        cnt = atoi(line);
    }
    pclose(fp);

    return (char)(cnt > 0);
}

static char is_exist_iscsi_mod()
{
    return __is_exist_mod(ISCSI_MOD);
}

static char is_exist_iscsi_sas_mod()
{
    return __is_exist_mod(ISCSI_SAS_MOD);
}

static char is_exist_iscsi_tp_mod()
{
    return __is_exist_mod(ISCSI_TP_MOD);
}

int main(int argc, char **argv)
{
    int err = -1;
    char iscsi, iscsi_tp, iscsi_sas;
    
    err = args_parse(argc, argv, "t:", &params);
    if (err != 0)
        return -1;

    printf("arg parse interval time:%us\n", params.period);

    iscsi = is_exist_iscsi_mod();
    iscsi_tp = is_exist_iscsi_tp_mod();
    iscsi_sas = is_exist_iscsi_sas_mod();

    INIT_BPF_APP(blockprobe);
    
    __LOAD_PROBE(blockprobe, err4, 1);
    __LOAD_PROBE(blockprobe_iscsi, err3, iscsi);
    __LOAD_PROBE(blockprobe_iscsi_tp, err2, iscsi_tp);
    __LOAD_PROBE(blockprobe_iscsi_sas, err, iscsi_sas);

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        goto err;
    }

    printf("Successfully started!\n");

    while (g_stop == 0) {
        sleep(params.period);
    }

err:
    if (iscsi_sas) {
        UNLOAD(blockprobe_iscsi_sas);
    }
err2:
    if (iscsi_tp) {
        UNLOAD(blockprobe_iscsi_tp);
    }
err3:
    if (iscsi) {
        UNLOAD(blockprobe_iscsi);
    }
err4:
    UNLOAD(blockprobe);
    return -err;
}
