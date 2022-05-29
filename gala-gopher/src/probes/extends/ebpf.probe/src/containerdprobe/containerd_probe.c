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
#include "hash.h"
#include "container.h"
#include "containerd_probe.skel.h"
#include "containerd_probe.h"

#define METRIC_NAME_RUNC_TRACE    "container_data"

static struct probe_params params = {.period = DEFAULT_PERIOD,
                                     .elf_path = {0}};
static volatile bool g_stop = false;
static void sig_handler(int sig)
{
    g_stop = true;
}

struct container_hash_t {
    H_HANDLE;
    struct container_key k;
    struct container_value v;
};

struct container_hash_t *head = NULL;

static void clear_container_tbl(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;
    if (*pphead == NULL)
        return;

    H_ITER(*pphead, item, tmp) {
        H_DEL(*pphead, item);
        (void)free(item);
    }
}

static struct container_hash_t* add_container(const char *container_id, struct container_hash_t **pphead)
{
    struct container_hash_t *item;

    INFO("Create new container %s.\n", container_id);

    item = malloc(sizeof(struct container_hash_t));
    if (item == NULL)
        return NULL;

    (void)memset(item, 0, sizeof(struct container_hash_t));
    (void)strncpy(item->k.container_id, container_id, CONTAINER_ID_LEN);

    H_ADD_KEYPTR(*pphead, item->k.container_id, CONTAINER_ID_LEN + 1, item);
    return item;
}

static struct container_hash_t* find_container(const char *container_id, struct container_hash_t **pphead)
{
    struct container_hash_t *item;

    H_FIND(*pphead, container_id, CONTAINER_ID_LEN + 1, item);
    return item;
}

static void delete_container(const char *container_id, struct container_hash_t **pphead)
{
    struct container_hash_t *item;

    INFO("Delete container %s.\n", container_id);

    item = find_container(container_id, pphead);
    if (item == NULL)
        return;

    H_DEL(*pphead, item);
    (void)free(item);
    return;
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

    (void)bpf_map_update_elem(fd, &sym_key, &symaddrs, BPF_ANY);
}

static void proc_container_evt(void *ctx, int cpu, void *data, __u32 size)
{
    struct container_evt_s *evt  = (struct container_evt_s *)data;
    struct container_hash_t *item;

    item = find_container((const char *)(evt->k.container_id), &head);
    if (evt->crt_or_del == 0) {
        if (item == NULL) {
            item = add_container((const char *)(evt->k.container_id), &head);
        }

        if (item) {
            item->v.task_pid = evt->task_pid;
            item->v.tgid = evt->tgid;
            (void)strncpy(item->v.comm, evt->comm, TASK_COMM_LEN - 1);
            // (void)strncpy(item->v.namespace, evt->namespace, NAMESPACE_LEN + 1);
        }
    } else {
        if (item) {
            delete_container((const char *)(evt->k.container_id), &head);
        }
    }
}

static void print_container_metric(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;
    struct cgroup_metric cgroup;

    H_ITER(*pphead, item, tmp) {
        get_container_cgroup_metric((char *)item->k.container_id, (char *)item->v.namespace, &cgroup);

        (void)get_cgroup_id_bypid(item->v.task_pid, &item->v.cgpid);

        item->v.memory_usage_in_bytes = cgroup.memory_usage_in_bytes;
        item->v.memory_limit_in_bytes = cgroup.memory_limit_in_bytes;
        item->v.memory_stat_cache = cgroup.memory_stat_cache;
        item->v.cpuacct_usage = cgroup.cpuacct_usage;
        item->v.pids_current = cgroup.pids_current;
        item->v.pids_limit = cgroup.pids_limit;

        fprintf(stdout, "|%s|%s|%u|%u|%llu|%llu|%llu|%llu|%llu|%llu|\n",
            METRIC_NAME_RUNC_TRACE,
            item->k.container_id,
            item->v.cgpid,
            item->v.task_pid,
            item->v.memory_usage_in_bytes,
            item->v.memory_limit_in_bytes,
            item->v.memory_stat_cache,
            item->v.cpuacct_usage,
            item->v.pids_current,
            item->v.pids_limit);
    }
    (void)fflush(stdout);
    return;
}

static void update_current_containers_info(struct container_hash_t **pphead)
{
    int i;
    struct container_hash_t *item;

    container_tbl* cstbl = get_all_container();
    if (cstbl != NULL) {
        container_info *p = cstbl->cs;
        for (i = 0; i < cstbl->num; i++) {
            if (p->status != CONTAINER_STATUS_RUNNING)
                continue;

            item = add_container(p->containerId, pphead);
            if (item) {
                item->v.task_pid = p->pid;
                item->v.cgpid = p->cgroup;
            }
            p++;
        }
        free_container_tbl(&cstbl);
    }
}

int main(int argc, char **argv)
{
    int err = -1;
    int ret = 0;
    char *elf[PATH_NUM] = {0};
    int elf_num = -1;
    int attach_flag = 0;
    int out_put_fd;
    struct perf_buffer* pb = NULL;

    err = args_parse(argc, argv, &params);
    if (err != 0)
        return -1;

    printf("arg parse interval time:%us  elf's path:%s\n", params.period, params.elf_path);

    /* Find elf's abs_path */
    ELF_REAL_PATH(containerd, params.elf_path, NULL, elf, elf_num);
    if (elf_num <= 0)
        return -1;

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
    /* load bpf prog */
    INIT_BPF_APP(containerd_probe, EBPF_RLIM_LIMITED);
    LOAD(containerd_probe, err);
    /* Update already running container */
    update_current_containers_info(&head);
    /* Update BPF symaddrs for this binary */
    bpf_update_containerd_symaddrs(GET_MAP_FD(containerd_probe, containerd_symaddrs_map));

    /* Attach tracepoint handler for each elf_path */
    for (int i = 0; i < elf_num; i++) {
        ret = 0;
        UBPF_ATTACH(containerd_probe, linux_Task_Start, elf[i], 
                github.com/containerd/containerd/runtime/v1/linux.(*Task).Start, ret);
        if (ret <= 0) {
            continue;
        }
        UBPF_ATTACH(containerd_probe, linux_Task_Delete, elf[i], 
                github.com/containerd/containerd/runtime/v1/linux.(*Task).Delete, ret);
        if (ret <= 0) {
            continue;
        }
        attach_flag = 1;
    }
    free_exec_path_buf(elf, elf_num);
    if (attach_flag == 0) {
        goto err;
    }

    out_put_fd = GET_MAP_FD(containerd_probe, output);
    pb = create_pref_buffer(out_put_fd, proc_container_evt);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    printf("Successfully started!\n");
    while (!g_stop) {
        if ((ret = perf_buffer__poll(pb, THOUSAND)) < 0)
            break;

        print_container_metric(&head);
        sleep(params.period);
    }
err:
    if (pb)
        perf_buffer__free(pb);

    /* Clean up */
    UNLOAD(containerd_probe);
    clear_container_tbl(&head);
    return -err;
}
