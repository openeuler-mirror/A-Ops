/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: luzhihao
 * Create: 2022-06-6
 * Description: nsprobe user prog
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
#include "qdisc.skel.h"
#include "qdisc.h"
#include "containerd_probe.h"
#include "object.h"
#include "nsprobe.h"

#define QDISC "qdisc"
#define QDISC_CPU "qdisc_cpu"

#define OUTPUT_PATH "/sys/fs/bpf/probe/__nsprobe_output"
#define ARGS_PATH "/sys/fs/bpf/probe/__nsprobe_args"
#define RM_BPF_PATH "/usr/bin/rm -rf /sys/fs/bpf/probe/__nsprobe*"

#define __LOAD_NS_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, output, OUTPUT_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, args_map, ARGS_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static struct probe_params params = {.period = DEFAULT_PERIOD};
static volatile sig_atomic_t g_stop;

static void sig_int(int signo)
{
    g_stop = 1;
}

static void print_ns_metrics(void *ctx, int cpu, void *data, __u32 size)
{
    struct qdisc *qdisc  = (struct qdisc *)data;

    (void)fprintf(stdout,
        "|%s|%u|%u|%s|%s|%u|%u|%u|%u|%u|%u|\n",
        QDISC,
        qdisc->handle,
        qdisc->ifindex,
        qdisc->dev_name,
        qdisc->kind,
        qdisc->netns_id,
        qdisc->egress.qlen,
        qdisc->egress.backlog,
        qdisc->egress.drops,
        qdisc->egress.requeues,
        qdisc->egress.overlimits);
}

static void load_args(int args_fd, struct probe_params* params)
{
    __u32 key = 0;
    struct ns_args_s args = {0};

    args.period = NS(params->period);

    (void)bpf_map_update_elem(args_fd, &key, &args, BPF_ANY);
}

int main(int argc, char **argv)
{
    int err = -1;
    struct perf_buffer* pb = NULL;
    FILE *fp = NULL;
    int task_map_fd;

    fp = popen(RM_BPF_PATH, "r");
    if (fp != NULL) {
        (void)pclose(fp);
        fp = NULL;
    }

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %d\n", errno);
        return errno;
    }

    err = args_parse(argc, argv, &params);
    if (err != 0) {
        return -1;
    }

    printf("arg parse interval time:%us\n", params.period);

    INIT_BPF_APP(nsprobe, EBPF_RLIM_LIMITED);
    __LOAD_NS_PROBE(qdisc, err, 1);

    task_map_fd = GET_MAP_FD(qdisc, __task_map);
    load_args(GET_MAP_FD(qdisc, args_map), &params);
    pb = create_pref_buffer(GET_MAP_FD(qdisc, output), print_ns_metrics);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    printf("Successfully started!\n");
    obj_module_init();

    while (!g_stop) {
        if ((err = perf_buffer__poll(pb, THOUSAND)) < 0) {
            break;
        }
        output_containers_info(&params, task_map_fd);
        sleep(params.period);
    }

err:
    if (pb) {
        perf_buffer__free(pb);
    }
    UNLOAD(qdisc);
    free_containers_info();
    obj_module_exit();
    return -err;
}
