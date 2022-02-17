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
 * Author: luzhihao
 * Create: 2022-02-10
 * Description: Collecting Task I/O Data
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"

#define MAX_CPU 8
#define TASK_REQUEST_MAX 100

#define REQ_OP_BITS 8
#define REQ_OP_MASK ((1 << REQ_OP_BITS) - 1)

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") task_request_start = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct request *),
    .value_size = sizeof(u64),
    .max_entries = TASK_REQUEST_MAX,
};

static __always_inline void update_task_count_entry(struct task_data *data, struct request *request, 
                                                                u64 delta_us, int rwflag)
{
    struct gendisk *gd;

    __sync_fetch_and_add(&(data->io.task_io_count), 1);
    __sync_fetch_and_add(&(data->io.task_io_time_us), delta_us);
    
    gd = _(request->rq_disk);
    data->io.major = _(gd->major);
    data->io.minor = _(gd->first_minor);
    
    if (rwflag) {
        // __sync_fetch_and_add(&(io_statsp->write_bytes), _(request->__data_len));
    } else {
        // __sync_fetch_and_add(&(io_statsp->read_bytes), _(request->__data_len));
    }
}

KPROBE(blk_mq_start_request, pt_regs)
{
    int pid;

    pid = bpf_get_current_pid_tgid() >> 32;
    if (!is_task_exist(pid)) {
        return;
    }
    
    u64 ts = bpf_ktime_get_ns();
    struct request *request = (struct request *)PT_REGS_PARM1(ctx);

    (void)bpf_map_update_elem(&task_request_start, &request, &ts, BPF_ANY);
}

KPROBE(blk_account_io_completion, pt_regs)
{
    int rwflag = 0;
    struct task_key key = {0};
    struct task_data *data;
    u64 *tsp;
    struct request *request = (struct request *)PT_REGS_PARM1(ctx);

    tsp = (u64 *)bpf_map_lookup_elem(&task_request_start, &request);
    if (tsp == (u64*)0) {
        return;
    }

    u64 delta_us = (bpf_ktime_get_ns() - *tsp) / 1000;

    key.pid = bpf_get_current_pid_tgid() >> 32;
    data = (struct task_data *)bpf_map_lookup_elem(&__task_map, &key);

    rwflag = !!((request->cmd_flags & REQ_OP_MASK) == REQ_OP_WRITE);
    
    if (data != (struct task_data *)0) {
        update_task_count_entry(data, request, delta_us, rwflag);
    }
}

struct bpf_map_def SEC("maps") task_io_wait = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct task_key),
    .value_size = sizeof(u64),
    .max_entries = MAX_CPU,
};

static __always_inline void __add_iowait(struct task_key *key, u64 delta_us)
{
    struct task_data *data = bpf_map_lookup_elem(&__task_map, key);
    if (data) {
        __sync_fetch_and_add(&data->io.task_io_wait_time_us, delta_us);
    }
}

KPROBE(io_schedule_prepare, pt_regs)
{
    struct task_key key = {0};
    u64 us = 0;
    
    key.pid = bpf_get_current_pid_tgid() >> 32;
    if (bpf_map_lookup_elem(&task_io_wait, &key) == 0) {
        us = bpf_ktime_get_ns() >> 3;
        (void)bpf_map_update_elem(&task_io_wait, &key, &us, BPF_ANY);
    }
}

KPROBE(io_schedule_finish, pt_regs)
{
    struct task_key key = {0};
    key.pid = bpf_get_current_pid_tgid() >> 32;
    u64* us = bpf_map_lookup_elem(&task_io_wait, &key);
    if (us) {
        u64 ts = bpf_ktime_get_ns();
        *us = (ts >> 3) - *us;
        __add_iowait(&key, *us);
        (void)bpf_map_delete_elem(&task_io_wait, &key);
    }
}

