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
#include "output.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") probe_proc_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct probe_process),
    .value_size = sizeof(int),
    .max_entries = PROBE_PROC_MAP_ENTRY_SIZE,
};

static __always_inline int get_task_pgid(const struct task_struct *cur_task)
{
    int pgid = 0;

    /* ns info from thread_pid */
    struct pid *thread_pid = _(cur_task->thread_pid);
    struct pid_namespace *ns_info = (struct pid_namespace *)0;
    if (thread_pid != 0) {
        int l = _(thread_pid->level);
        struct upid thread_upid = _(thread_pid->numbers[l]);
        ns_info = thread_upid.ns;
    }

    /* upid info from signal */
    struct signal_struct* signal = _(cur_task->signal);
    struct pid *pid_p = (struct pid *)0;
    bpf_probe_read(&pid_p, sizeof(struct pid *), &signal->pids[PIDTYPE_PGID]);
    int level = _(pid_p->level);
    struct upid upid = _(pid_p->numbers[level]);
    if (upid.ns == ns_info) {
        pgid = upid.nr;
    }

    return pgid;
}

static __always_inline int is_task_in_probe_range(const struct task_struct *task)
{
    int flag = 0;
    struct probe_process pname = {0};

    bpf_probe_read_str(&pname.name, TASK_COMM_LEN * sizeof(char), (char *)task->comm);
    struct mm_struct *mm = _(task->mm);
    if (mm == (struct mm_struct *)0) {
        /* is kthread */
        if (pname.name[0] == 's' && pname.name[1] == 'c' && pname.name[2] == 's' && pname.name[3] == 'i') {
            /* scsi */
            flag = 1;
        } else if (pname.name[0] == 's' && pname.name[1] == 'o' && pname.name[2] == 'f' && pname.name[3] == 't' &&
                    pname.name[4] == 'i' && pname.name[5] == 'r' && pname.name[6] == 'q') {
            /* softirq */
            flag = 1;
        } else if (pname.name[0] == 'k' && pname.name[1] == 'w' && pname.name[2] == 'o' && pname.name[3] == 'r' &&
                    pname.name[4] == 'k' && pname.name[5] == 'e' && pname.name[6] == 'r') {
            /* kworker */
            flag = 1;
        } else {
            ;
        }
    } else {
        char *buf = (char *)bpf_map_lookup_elem(&probe_proc_map, &pname);
        if (buf != (char *)0) {
            flag = *buf;
        }
    }
    return flag;
}

KRAWTRACE(sched_process_fork, bpf_raw_tracepoint_args)
{
    struct task_key parent_key = {0};
    struct task_key child_key = {0};
    struct task_data *parent_data_p;
    struct task_data task_value = {0};

    struct task_struct* parent = (struct task_struct*)ctx->args[0];
    struct task_struct* child = (struct task_struct*)ctx->args[1];

    /* check whether task in probe_range */
    int flag = is_task_in_probe_range(child);

    /* if task in probe_range, update info to task_map */
    if (flag == 1) {
        /* Add child task info to task_map */
        child_key.pid = _(child->pid);
        task_value.id.pid = child_key.pid;
        task_value.id.tgid = _(child->tgid);
        task_value.id.ppid = _(parent->pid);
        task_value.id.pgid = get_task_pgid(child);
        bpf_probe_read_str(&task_value.id.comm, TASK_COMM_LEN * sizeof(char), (char *)child->comm);
        upd_task_entry(&child_key, &task_value);

        /* obtain parent task info */
        parent_key.pid = task_value.id.ppid;
        parent_data_p = (struct task_data *)get_task_entry(&parent_key);
        if (parent_data_p != (struct task_data *)0) {
            /* fork_count add 1 */
            __sync_fetch_and_add(&parent_data_p->fork_count, 1);
        } else {
            /* Add parent's task info to task_map first time */
            task_value.id.pid = parent_key.pid;
            task_value.id.tgid = _(parent->tgid);
            task_value.id.ppid = -1;
            bpf_probe_read_str(&task_value.id.comm, TASK_COMM_LEN * sizeof(char), (char *)parent->comm);
            task_value.fork_count = 1;
            upd_task_entry(&parent_key, &task_value);
        }
    }
}

KRAWTRACE(sched_process_exit, bpf_raw_tracepoint_args)
{
    struct task_struct* task = (struct task_struct*)ctx->args[0];
    struct task_key k = {0};

    k.pid = _(task->pid);
    del_task_entry(&k);
}

KRAWTRACE(task_rename, bpf_raw_tracepoint_args)
{
    struct task_struct* task = (struct task_struct *)ctx->args[0];
    const char *comm = (const char *)ctx->args[1];

    struct task_key key = {.pid = _(task->pid)};
    struct task_data *val = (struct task_data *)get_task_entry(&key);
    if (val) {
        bpf_probe_read_str(&(val->id.comm), TASK_COMM_LEN * sizeof(char), (char *)comm);
        upd_task_entry(&key, val);
    }
}
