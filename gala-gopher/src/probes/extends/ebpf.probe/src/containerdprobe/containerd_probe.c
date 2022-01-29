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
 * Author: dowzyx
 * Create: 2021-12-04
 * Description: container_probe user prog
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "container.h"
#include "containerd_probe.skel.h"
#include "containerd_probe.h"

#define METRIC_NAME_RUNC_TRACE    "container_data"
#define CONTAINERS_MAP_FILE_PATH  "/sys/fs/bpf/probe/containers"

static struct probe_params params = {.period = DEFAULT_PERIOD,
                                     .elf_path = {0}};
static volatile bool g_stop = false;
static void sig_handler(int sig)
{
    g_stop = true;
}

static void bpf_update_containerd_symaddrs(int fd)
{
    struct go_containerd_t symaddrs = {0};
    unsigned int sym_key = SYMADDRS_MAP_KEY;

    // Arguments of runtime/v1/linux.(*Task).Start.
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L120
    symaddrs.task_Start_t_offset            = 8;
    // Arguments of runtime/v1/linux.(*Task).Delete.
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L88
    symaddrs.task_Delete_t_offset           = 8;
    symaddrs.task_Delete_resp_offset        = 24;
    // Members of /runtime/v1/linux.Task
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L42
    symaddrs.linux_Task_id_offset           = 8;
    symaddrs.linux_Task_pid_offset          = 24;
    symaddrs.linux_Task_namespace_offset    = 40;
    symaddrs.linux_Task_cg_offset           = 56;
    // Members of /runtime.Exit
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/runtime.go#L54
    symaddrs.runtime_Exit_Pid_offset        = 0;
    symaddrs.runtime_Exit_Status_offset     = 4;
    symaddrs.runtime_Exit_Timestamp_offset  = 8;

    bpf_map_update_elem(fd, &sym_key, &symaddrs, BPF_ANY);
}

static void print_container_metric(int fd)
{
    int ret = -1;
    struct container_key    k  = {0};
    struct container_key    nk = {0};
    struct container_value  v  = {0};

    while (bpf_map_get_next_key(fd, &k, &nk) != -1) {
        ret = bpf_map_lookup_elem(fd, &nk, &v);
        if (ret == 0) {
            /* add container's cgroup metrics when container start */
            if (v.memory_usage_in_bytes == 0) {
                struct cgroup_metric   cgroup = {0};
                get_container_cgroup_metric((char *)nk.container_id, (char *)v.namespace, &cgroup);
                v.memory_usage_in_bytes = cgroup.memory_usage_in_bytes;
                v.memory_limit_in_bytes = cgroup.memory_limit_in_bytes;
                v.memory_stat_cache = cgroup.memory_stat_cache;
                v.cpuacct_usage = cgroup.cpuacct_usage;
                v.pids_current = cgroup.pids_current;
                v.pids_limit = cgroup.pids_limit;
                /* update hash map */
                bpf_map_update_elem(fd, &nk, &v, BPF_ANY);
            }
            fprintf(stdout, "|%s|%s|%s|%u|%llu|%llu|%llu|%llu|%llu|%llu|%u|\n",
                METRIC_NAME_RUNC_TRACE,
                nk.container_id,
                v.namespace,
                v.task_pid,
                v.memory_usage_in_bytes,
                v.memory_limit_in_bytes,
                v.memory_stat_cache,
                v.cpuacct_usage,
                v.pids_current,
                v.pids_limit,
                v.status);
        }
        if (v.status == 0) {
            bpf_map_delete_elem(fd, &nk);
        } else {
            k = nk;
        }
    }
    (void)fflush(stdout);
    return;
}

static void update_current_containers_info(int map_fd)
{
    int ret;
    int i;
    struct container_value c_value = {0};

    container_tbl* cstbl = get_all_container();
    if (cstbl != NULL) {
        container_info *p = cstbl->cs;
        for (i = 0; i < cstbl->num; i++) {
            ret = bpf_map_lookup_elem(map_fd, p->container, &c_value);
            if (ret) {
                c_value.task_pid = p->pid;
                c_value.status = 1;
                bpf_map_update_elem(map_fd, p->container, &c_value, BPF_ANY);
            }
            p++;
        }
        free_container_tbl(&cstbl);
    }
}

int main(int argc, char **argv)
{
    int err = -1;
    char *elf[PATH_NUM] = {0};
    int elf_num = -1;
    int attach_flag = 0;

    err = args_parse(argc, argv, "t:p:", &params);
    if (err != 0)
        return -1;

    printf("arg parse interval time:%us  elf's path:%s\n", params.period, params.elf_path);
    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
    /* load bpf prog */
    LOAD(containerd_probe);
    /* Update already running container */
    update_current_containers_info(GET_MAP_FD(containers_map));
    /* Update BPF symaddrs for this binary */
    bpf_update_containerd_symaddrs(GET_MAP_FD(containerd_symaddrs_map));
    /* Find elf's abs_path */
    ELF_REAL_PATH(containerd, params.elf_path, NULL, elf, elf_num);
    if (elf_num <= 0)
        return -1;

    /* Attach tracepoint handler for each elf_path */
    for (int i = 0; i < elf_num; i++) {
        int ret = 0;
        UBPF_ATTACH(linux_Task_Start, elf[i], github.com/containerd/containerd/runtime/v1/linux.(*Task).Start, ret);
        if (ret <= 0) {
            continue;
        }
        UBPF_ATTACH(linux_Task_Delete, elf[i], github.com/containerd/containerd/runtime/v1/linux.(*Task).Delete, ret);
        if (ret <= 0) {
            continue;
        }
        attach_flag = 1;
    }
    free_exec_path_buf(elf, elf_num);
    if (attach_flag == 0) {
        goto err;
    }

    int pinned = bpf_obj_pin(GET_MAP_FD(containers_map), CONTAINERS_MAP_FILE_PATH);
    if (pinned < 0) {
        printf("Failed to pin containers_map to the file system: %d, err: %d\n", pinned, errno);
        goto err;
    }
    while (!g_stop) {
        print_container_metric(GET_MAP_FD(containers_map));
        sleep(params.period);
    }
err:
    /* Clean up */
    UNLOAD(containerd_probe);
    if (access(CONTAINERS_MAP_FILE_PATH, F_OK) == 0) {
        if (remove(CONTAINERS_MAP_FILE_PATH) < 0)
            printf("Delete the pinned file:%s failed!\n", CONTAINERS_MAP_FILE_PATH);
    }
    return -err;
}
