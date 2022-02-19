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

struct bpf_map_def SEC("maps") probe_proc_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct probe_process),
    .value_size = sizeof(int),
    .max_entries = PROBE_PROC_MAP_ENTRY_SIZE,
};

static int get_task_pgid(const struct task_struct *cur_task)
{
    int pgid = 0;

    /* ns info from thread_pid */
    struct pid *thread_pid = _(cur_task->thread_pid);
    char *ns_info = (void *)0;
    if (thread_pid != 0) {
        int l = _(thread_pid->level);
        struct upid thread_upid = _(thread_pid->numbers[l]);
        ns_info = thread_upid.ns;
    }

    /* upid info from signal */
    struct signal_struct* signal = _(cur_task->signal);
    struct pid *pid_p = (void *)0;
    bpf_probe_read(&pid_p, sizeof(struct pid *), &signal->pids[PIDTYPE_PGID]);
    int level = _(pid_p->level);
    struct upid upid = _(pid_p->numbers[level]);
    if (upid.ns == ns_info) {
        pgid = upid.nr;
    }

    return pgid;
}

static void update_task_status(struct task_struct* task, __u32 task_status)
{
    struct task_key key = {0};
    struct task_data *data;
    
    key.pid = _(task->pid);
    data = (struct task_data *)get_task_entry(&key);
    if (data != (struct task_data *)0) {
        data->base.task_status = task_status;
    }
    return;
}

KRAWTRACE(sched_process_fork, bpf_raw_tracepoint_args)
{
    struct task_key parent_key = {0};
    struct task_key child_key = {0};
    struct task_data *parent_data_p;
    struct task_data task_value = {0};
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
        /* Add child task info to task_map */
        child_key.pid = _(child->pid);
        task_value.id.tgid = _(child->tgid);
        task_value.id.ppid = _(parent->pid);
        task_value.id.pgid = get_task_pgid(child);
        upd_task_entry(&child_key, &task_value);

        /* obtain parent task info */
        parent_key.pid = task_value.id.ppid;
        
        parent_data_p = (struct task_data *)get_task_entry(&parent_key);

        if (parent_data_p != (struct task_data *)0) {
            /* fork_count add 1 */
            __sync_fetch_and_add(&parent_data_p->base.fork_count, 1);
        } else {
            /* Add parent's task info to task_map first time */
            task_value.id.tgid = _(parent->tgid);
            task_value.id.ppid = -1;
            task_value.base.fork_count = 1;
            upd_task_entry(&parent_key, &task_value);
        }
    }
}

KRAWTRACE(sched_process_exit, bpf_raw_tracepoint_args)
{
    struct task_struct* task = (struct task_struct*)ctx->args[0];
    update_task_status(task, TASK_STATUS_INVALID);
}

