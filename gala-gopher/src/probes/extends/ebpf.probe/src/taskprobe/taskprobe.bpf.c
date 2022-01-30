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
 * Description: task_probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "taskprobe.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") task_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct task_key),
    .value_size = sizeof(struct task_kdata),
    .max_entries = TASK_MAP_ENTRY_SIZE,
};

struct bpf_map_def SEC("maps") task_exit_event = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(int),
    .value_size = sizeof(int),
};

KRAWTRACE(sched_process_fork, bpf_raw_tracepoint_args)
{
    struct task_key parent_key = {0};
    struct task_kdata *parent_data;
    struct task_key child_key = {0};
    struct task_kdata child_data = {0};

    struct task_struct* parent = (struct task_struct*)ctx->args[0];
    struct task_struct* child = (struct task_struct*)ctx->args[1];

    parent_key.tgid = _(parent->tgid);
    parent_key.pid = _(parent->pid);
    parent_data = bpf_map_lookup_elem(&task_map, &parent_key);
    if (parent_data != (void *)0) {
        __sync_fetch_and_add(&parent_data->fork_count, 1);
    }

    child_key.tgid = _(child->tgid);
    child_key.pid = _(child->pid);
    child_data.ptid = child_key.tgid;
    bpf_map_update_elem(&task_map, &child_key, &child_data, BPF_ANY);
}

KRAWTRACE(sched_process_exit, bpf_raw_tracepoint_args)
{
    struct task_key tkey = {0};
    struct task_struct* task = (struct task_struct*)ctx->args[0];

    tkey.tgid = _(task->tgid);
    tkey.pid = _(task->pid);
    if (bpf_map_delete_elem(&task_map, &tkey) == 0) {
        if (tkey.tgid == tkey.pid) {
            bpf_perf_event_output(ctx, &task_exit_event, 0, &tkey.tgid, sizeof(tkey.tgid));
        }
    }
}