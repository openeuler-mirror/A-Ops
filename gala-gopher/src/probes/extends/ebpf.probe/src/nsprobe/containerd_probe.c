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
 * Description: container traceing
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
#include "containerd_probe.h"

#define METRIC_NAME_RUNC_TRACE    "container_data"

static void init_container(const char *container_id, struct container_value *container)
{
    container->flags |= CONTAINER_FLAGS_VALID;

    if (container->proc_id == 0) {
        (void)get_container_pid(container_id, &container->proc_id);
    }

    if (container->name[0] == 0) {
        (void)get_container_name(container_id, container->name, CONTAINER_NAME_LEN);
    }

    if (container->cpucg_dir[0] == 0) {
        (void)get_container_cpucg_dir(container_id, container->cpucg_dir, PATH_LEN);
    }

    if (container->memcg_dir[0] == 0) {
        (void)get_container_memcg_dir(container_id, container->memcg_dir, PATH_LEN);
    }

    if (container->pidcg_dir[0] == 0) {
        (void)get_container_pidcg_dir(container_id, container->pidcg_dir, PATH_LEN);
    }

    if (container->cpucg_inode == 0) {
        (void)get_container_cpucg_inode(container_id, &container->cpucg_inode);
    }

    if (container->memcg_inode == 0) {
        (void)get_container_memcg_inode(container_id, &container->memcg_inode);
    }

    if (container->pidcg_inode == 0) {
        (void)get_container_pidcg_inode(container_id, &container->pidcg_inode);
    }

    if (container->mnt_ns_id == 0) {
        (void)get_container_mntns_id(container_id, &container->mnt_ns_id);
    }

    if (container->net_ns_id == 0) {
        (void)get_container_netns_id(container_id, &container->net_ns_id);
    }

    return;
}

struct container_hash_t {
    H_HANDLE;
    struct container_key k;
    struct container_value v;
};

static struct container_hash_t *head = NULL;

static void clear_container_tbl(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;
    if (*pphead == NULL) {
        return;
    }

    H_ITER(*pphead, item, tmp) {
        H_DEL(*pphead, item);
        (void)free(item);
    }
}

static void clear_invalid_items(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;
    if (*pphead == NULL) {
        return;
    }

    H_ITER(*pphead, item, tmp) {
        if (!(item->v.flags & CONTAINER_FLAGS_VALID)) {
            H_DEL(*pphead, item);
            (void)free(item);
        }
    }
}

static void set_container_invalid(struct container_hash_t **pphead)
{
    struct container_hash_t *item, *tmp;
    if (*pphead == NULL) {
        return;
    }

    H_ITER(*pphead, item, tmp) {
        item->v.flags &= ~CONTAINER_FLAGS_VALID;
    }
}

static struct container_hash_t* add_container(const char *container_id, struct container_hash_t **pphead)
{
    struct container_hash_t *item;

    INFO("Create new container %s.\n", container_id);

    item = malloc(sizeof(struct container_hash_t));
    if (item == NULL) {
        return NULL;
    }

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

#ifdef COMMAND_LEN
#undef COMMAND_LEN
#define COMMAND_LEN 512
#endif

#ifndef __CAT_FILE
#define __CAT_FILE "/usr/bin/cat %s/%s"
#endif

#ifndef __TEN
#define __TEN 10
#endif
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
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }
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
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }

    container->cpuacct_usage = strtoull((char *)line, NULL, __TEN);

    /* cpuacct.usage_sys */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->cpucg_dir, "cpuacct.usage_sys");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }

    container->cpuacct_usage_sys = strtoull((char *)line, NULL, __TEN);

    /* cpuacct.usage_user */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->cpucg_dir, "cpuacct.usage_user");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }

    container->cpuacct_usage_user = strtoull((char *)line, NULL, __TEN);

    return;
}

#ifndef PID_MAX_LIMIT
#define PID_MAX_LIMIT 2^22
#endif
static void __get_container_pids_metrics(struct container_value *container)
{
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    /* pids.current */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->pidcg_dir, "pids.current");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }

    container->pids_current = strtoull((char *)line, NULL, __TEN);

    /* pids.limit */
    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, __CAT_FILE, container->pidcg_dir, "pids.max");
    if (exec_cmd(command, line, LINE_BUF_LEN) == -1) {
        return;
    }

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

        (void)fprintf(stdout, "|%s|%s|%s|%u|%u|%u|%u|%u|%u|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
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
    struct container_hash_t* item;

    set_container_invalid(pphead);

    container_tbl* cstbl = get_all_container();
    if (cstbl != NULL) {
        container_info *p = cstbl->cs;
        for (i = 0; i < cstbl->num; i++) {
            if (p->status != CONTAINER_STATUS_RUNNING) {
                p++;
                continue;
            }

            item = find_container((const char *)p->abbrContainerId, pphead);
            if (item == NULL) {
                (void)add_container(p->abbrContainerId, pphead);
            } else {
                item->v.flags |= CONTAINER_FLAGS_VALID;
            }

            p++;
        }
        free_container_tbl(&cstbl);
    }

    clear_invalid_items(pphead);
}

void output_containers_info(void)
{
    update_current_containers_info(&head);
    print_container_metric(&head);
}

void free_containers_info(void)
{
    clear_container_tbl(&head);
}

