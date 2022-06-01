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

static void init_container(const char *container_id, struct container_value *container)
{
    if (container->proc_id == 0)
        (void)get_container_pid(container_id, &container->proc_id);

    if (container->name[0] == 0)
        (void)get_container_name(container_id, container->name, CONTAINER_NAME_LEN);

    if (container->cpucg_dir[0] == 0)
        (void)get_container_cpucg_dir(container_id, container->cpucg_dir, PATH_LEN);

    if (container->memcg_dir[0] == 0)
        (void)get_container_memcg_dir(container_id, container->memcg_dir, PATH_LEN);

    if (container->pidcg_dir[0] == 0)
        (void)get_container_pidcg_dir(container_id, container->pidcg_dir, PATH_LEN);

    if (container->cpucg_inode == 0)
        (void)get_container_cpucg_inode(container_id, &container->cpucg_inode);

    if (container->memcg_inode == 0)
        (void)get_container_memcg_inode(container_id, &container->memcg_inode);

    if (container->pidcg_inode == 0)
        (void)get_container_pidcg_inode(container_id, &container->pidcg_inode);

    if (container->mnt_ns_id == 0)
        (void)get_container_mntns_id(container_id, &container->mnt_ns_id);

    if (container->net_ns_id == 0)
        (void)get_container_netns_id(container_id, &container->net_ns_id);

    return;
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
    (void)strncpy(item->k.container_id, container_id, CONTAINER_ABBR_ID_LEN);

    H_ADD_KEYPTR(*pphead, item->k.container_id, CONTAINER_ABBR_ID_LEN, item);

    init_container((const char *)item->k.container_id, &(item->v));
    return item;
}

static struct container_hash_t* find_container(const char *container_id, struct container_hash_t **pphead)
{
    struct container_hash_t *item;

    H_FIND(*pphead, container_id, CONTAINER_ABBR_ID_LEN, item);
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
    } else {
        if (item) {
            delete_container((const char *)(evt->k.container_id), &head);
        }
    }
}

#ifdef COMMAND_LEN
#undef COMMAND_LEN
#define COMMAND_LEN 512
#endif

#define __CAT_FILE "/usr/bin/cat %s/%s"
#define __TEN 10
static void __get_container_memory_metrics(struct container_value *container)
{
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    /* memory.usage_in_bytes */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->memcg_dir, "memory.usage_in_bytes");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }
    container->memory_usage_in_bytes = strtoull((char *)line, NULL, __TEN);

    /* memory.limit_in_bytes */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->memcg_dir, "memory.limit_in_bytes");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;
    container->memory_limit_in_bytes = strtoull((char *)line, NULL, __TEN);

    return;
}

static void __get_container_cpuaccet_metrics(struct container_value *container)
{
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    /* cpuacct.usage */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->cpucg_dir, "cpuacct.usage");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;

    container->cpuacct_usage = strtoull((char *)line, NULL, __TEN);

    /* cpuacct.usage_sys */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->cpucg_dir, "cpuacct.usage_sys");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;

    container->cpuacct_usage_sys = strtoull((char *)line, NULL, __TEN);

    /* cpuacct.usage_user */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->cpucg_dir, "cpuacct.usage_user");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;

    container->cpuacct_usage_user = strtoull((char *)line, NULL, __TEN);

    return;
}

#define PID_MAX_LIMIT 2^22
static void __get_container_pids_metrics(struct container_value *container)
{
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    /* pids.current */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->pidcg_dir, "pids.current");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;

    container->pids_current = strtoull((char *)line, NULL, __TEN);

    /* pids.limit */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->pidcg_dir, "pids.max");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1)
        return;

    if (strcmp((char *)line, "max") == 0) {
        container->pids_limit = PID_MAX_LIMIT;
    } else {
        container->pids_limit = strtoull((char *)line, NULL, __TEN);
    }

    return;
}

static void print_container_metric(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;

    H_ITER(*pphead, item, tmp) {
        __get_container_memory_metrics(&(item->v));
        __get_container_cpuaccet_metrics(&(item->v));
        __get_container_pids_metrics(&(item->v));

        fprintf(stdout, "|%s|%s|%s|%u|%u|%u|%u|%u|%u|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
            METRIC_NAME_RUNC_TRACE,
            item->k.container_id,
            item->v.name,
            item->v.cpucg_inode,
            item->v.memcg_inode,
            item->v.pidcg_inode,
            item->v.mnt_ns_id,
            item->v.net_ns_id,
            item->v.proc_id,
            item->v.memory_usage_in_bytes,
            item->v.memory_limit_in_bytes,
            item->v.cpuacct_usage,
            item->v.cpuacct_usage_sys,
            item->v.cpuacct_usage_user,
            item->v.pids_current,
            item->v.pids_limit);
    }
    (void)fflush(stdout);
    return;
}

static void update_current_containers_info(struct container_hash_t **pphead)
{
    int i;

    container_tbl* cstbl = get_all_container();
    if (cstbl != NULL) {
        container_info *p = cstbl->cs;
        for (i = 0; i < cstbl->num; i++) {
            if (p->status != CONTAINER_STATUS_RUNNING)
                continue;

            (void)add_container(p->abbrContainerId, pphead);
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
