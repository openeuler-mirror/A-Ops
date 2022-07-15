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
 * Create: 2022-07-13
 * Description: output of proc
 ******************************************************************************/
#ifndef __OUTPUT_PROC_H__
#define __OUTPUT_PROC_H__

#pragma once

#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "args_map.h"
#include "proc.h"

#define BPF_F_INDEX_MASK    0xffffffffULL
#define BPF_F_CURRENT_CPU   BPF_F_INDEX_MASK

#define PERF_OUT_MAX (64)
struct bpf_map_def SEC("maps") g_proc_output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = PERF_OUT_MAX,
};

static __always_inline __maybe_unused void report_proc(void *ctx, struct proc_data_s *proc)
{
    u64 ts = bpf_ktime_get_ns();
    u64 period = get_period();
    if ((ts > proc->ts) && ((ts - proc->ts) < period)) {
        return;
    }
    proc->ts = ts;
    (void)bpf_perf_event_output(ctx, &g_proc_output, BPF_F_CURRENT_CPU, proc, sizeof(struct proc_data_s));

    proc->fs_op_start_ts = 0;
    __builtin_memset(&(proc->syscall), 0x0, sizeof(proc->syscall));
    __builtin_memset(&(proc->op_ext4), 0x0, sizeof(proc->op_ext4));
    __builtin_memset(&(proc->op_overlay), 0x0, sizeof(proc->op_overlay));
    __builtin_memset(&(proc->op_tmpfs), 0x0, sizeof(proc->op_tmpfs));
    __builtin_memset(&(proc->page_op), 0x0, sizeof(proc->page_op));
    __builtin_memset(&(proc->dns_op), 0x0, sizeof(proc->dns_op));
}

#endif
