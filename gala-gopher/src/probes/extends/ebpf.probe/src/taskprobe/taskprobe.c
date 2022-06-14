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
 * Author: sinever
 * Create: 2021-10-25
 * Description: task_probe user prog
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
#include "taskprobe.skel.h"
#include "thread_io.skel.h"
#include "taskprobe.h"
#include "task.h"

#define OO_THREAD_NAME  "thread"
#define OUTPUT_PATH "/sys/fs/bpf/probe/__taskprobe_output"
#define PERIOD_PATH "/sys/fs/bpf/probe/__taskprobe_period"

#define LOAD_TASK_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, output, OUTPUT_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, period_map, PERIOD_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static volatile sig_atomic_t stop = 0;
static struct probe_params tp_params = {.period = DEFAULT_PERIOD,
                                        .task_whitelist = {0}};

static struct task_name_t task_range[] = {
    {"go",              TASK_TYPE_APP},
    {"java",            TASK_TYPE_APP},
    {"python",          TASK_TYPE_APP},
    {"python3",         TASK_TYPE_APP},
    {"dhclient",        TASK_TYPE_OS},
    {"NetworkManager",  TASK_TYPE_OS},
    {"dbus",            TASK_TYPE_OS},
    {"rpcbind",         TASK_TYPE_OS},
    {"systemd",         TASK_TYPE_OS},
    {"scsi",            TASK_TYPE_KERN},
    {"softirq",         TASK_TYPE_KERN},
    {"kworker",         TASK_TYPE_KERN}
};

static void sig_int(int signal)
{
    stop = 1;
}

static void load_daemon_task(int app_fd, int task_map_fd)
{
    struct probe_process ckey = {0};
    struct probe_process nkey = {0};
    int flag;
    int ret = -1;

    while (bpf_map_get_next_key(app_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(app_fd, &nkey, &flag);
        if (ret == 0) {
            load_daemon_task_by_name(task_map_fd, (const char *)nkey.name, 1);
            DEBUG("[TASKPROBE]: load daemon process '%s'.\n", nkey.name);
        }
        ckey = nkey;
    }

    uint32_t index, size = sizeof(task_range) / sizeof(task_range[0]);
    for (index = 0; index < size; index++) {
        if (task_range[index].type != TASK_TYPE_APP) {

            load_daemon_task_by_name(task_map_fd, (const char *)task_range[index].name, 0);
            DEBUG("[TASKPROBE]: load daemon process '%s'.\n", task_range[index].name);
        }
    }

    return;
}

static void load_task_range(int fd)
{
    int flag = 1;
    struct probe_process pname;
    uint32_t index = 0;
    uint32_t size = sizeof(task_range) / sizeof(task_range[0]);

    for (index = 0; index < size; index++) {
        if (task_range[index].type == TASK_TYPE_APP || task_range[index].type == TASK_TYPE_OS) {
            (void)memset(pname.name, 0, TASK_COMM_LEN);
            (void)strncpy(pname.name, task_range[index].name, TASK_COMM_LEN - 1);

            /* update probe_proc_map */
            (void)bpf_map_update_elem(fd, &pname, &flag, BPF_ANY);

            DEBUG("[TASKPROBE]: load probe process name '%s'.\n", pname.name);
        }
    }
}

static void load_task_wl(int fd)
{
    FILE *f = NULL;
    char line[TASK_COMM_LEN];
    struct probe_process pname;
    int flag = 1;

    f = fopen(tp_params.task_whitelist, "r");
    if (f == NULL) {
        return;
    }
    while (!feof(f)) {
        (void)memset(line, 0, TASK_COMM_LEN);
        if (fgets(line, TASK_COMM_LEN, f) == NULL) {
            goto out;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        if (strlen(line) == 0) {
            continue;
        }
        (void)memset(pname.name, 0, TASK_COMM_LEN);
        (void)strncpy(pname.name, line, TASK_COMM_LEN - 1);

        /* update probe_proc_map */
        (void)bpf_map_update_elem(fd, &pname, &flag, BPF_ANY);

        DEBUG("[TASKPROBE]: load probe process name '%s'.\n", pname.name);
    }
out:
    fclose(f);
    return;
}

static void load_period(int period_fd, __u32 value)
{
    __u32 key = 0;
    __u64 period = NS(value);
    (void)bpf_map_update_elem(period_fd, &key, &period, BPF_ANY);
}
static void print_task_metrics(void *ctx, int cpu, void *data, __u32 size)
{
    struct task_data *value = (struct task_data *)data;

    fprintf(stdout,
        "|%s|%d|%d|%s|%d|%d|%u|%llu|%llu|%u|%llu|\n",
        OO_THREAD_NAME,
        value->id.pid,
        value->id.tgid,
        value->id.comm,
        value->io.major,
        value->io.minor,
        value->fork_count,
        value->io.task_io_count,
        value->io.task_io_time_us,
        value->io.task_hang_count,
        value->io.task_io_wait_time_us);

    (void)fflush(stdout);
    return;
}

int main(int argc, char **argv)
{
    int ret = -1;
    struct perf_buffer* pb = NULL;

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        return -1;
    }

    ret = args_parse(argc, argv, &tp_params);
    if (ret != 0) {
        return ret;
    }

    if (strlen(tp_params.task_whitelist) == 0) {
        fprintf(stderr, "***task_whitelist_path is null, please check param : -c xx/xxx *** \n");
    }
    DEBUG("Task probe starts with period: %us.\n", tp_params.period);

    INIT_BPF_APP(taskprobe, EBPF_RLIM_LIMITED);

    LOAD_TASK_PROBE(taskprobe, err2, 1);
    LOAD_TASK_PROBE(thread_io, err1, 1);

    int out_put_fd = GET_MAP_FD(taskprobe, output);
    pb = create_pref_buffer(out_put_fd, print_task_metrics);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    int pmap_fd = GET_MAP_FD(taskprobe, probe_proc_map);
    int task_map_fd = GET_MAP_FD(taskprobe, __task_map);
    int period_fd = GET_MAP_FD(taskprobe, period_map);

    load_period(period_fd, tp_params.period);

    load_task_range(pmap_fd);

    load_task_wl(pmap_fd);

    load_daemon_task(pmap_fd, task_map_fd);

    printf("Successfully started!\n");

    poll_pb(pb, THOUSAND);

err:
    if (pb) {
        perf_buffer__free(pb);
    }
err1:
    UNLOAD(thread_io);
err2:
    UNLOAD(taskprobe);
    return ret;
}
