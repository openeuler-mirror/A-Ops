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
#include "task.h"
#include "taskprobe.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") task_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct task_key),
    .value_size = sizeof(struct task_data),
    .max_entries = TASK_MAP_ENTRY_SIZE,
};

struct bpf_map_def SEC("maps") task_exit_event = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(int),
    .value_size = sizeof(int),
};

struct bpf_map_def SEC("maps") probe_proc_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct probe_process),
    .value_size = sizeof(int),
    .max_entries = PROBE_PROC_MAP_ENTRY_SIZE,
};

KRAWTRACE(sched_process_fork, bpf_raw_tracepoint_args)
{
    struct task_key parent_key = {0};
    struct task_data *parent_data;
    struct task_key child_key = {0};
    struct task_data child_data = {0};
    struct probe_process pname = {0};
    int flag = 0;

    struct task_struct* parent = (struct task_struct*)ctx->args[0];
    struct task_struct* child = (struct task_struct*)ctx->args[1];

    /* check whether process comm is in probe_process list */
    bpf_probe_read_str(&pname.name, MAX_PROCESS_NAME_LEN * sizeof(char), (char *)child->comm);
    char *buf = (char *)bpf_map_lookup_elem(&probe_proc_map, &pname);
    if (buf != (void *)0) {
        flag = *buf;
    }
    /* if process in whitelist, update info to task_map */
    if (flag == 1) {
        parent_key.pid = _(parent->pid);
        parent_data = bpf_map_lookup_elem(&task_map, &parent_key);
        if (parent_data != (void *)0) {
            __sync_fetch_and_add(&parent_data->fork_count, 1);
        }

        child_key.pid = _(child->pid);
        child_data.tgid = _(child->tgid);
        child_data.ptid = _(parent->tgid);
        bpf_probe_read_str(&child_data.comm, TASK_COMM_LEN * sizeof(char), (char *)child->comm);

        bpf_map_update_elem(&task_map, &child_key, &child_data, BPF_ANY);
    }
}

KRAWTRACE(sched_process_exit, bpf_raw_tracepoint_args)
{
    struct task_key tkey = {0};
    struct task_struct* task = (struct task_struct*)ctx->args[0];

    int tgid = bpf_get_current_pid_tgid() >> 32;
    tkey.pid = _(task->pid);
    if (bpf_map_delete_elem(&task_map, &tkey) == 0) {
        if (tgid == tkey.pid) {
            bpf_perf_event_output(ctx, &task_exit_event, 0, &tkey.pid, sizeof(tkey.pid));
        }
    }
}
