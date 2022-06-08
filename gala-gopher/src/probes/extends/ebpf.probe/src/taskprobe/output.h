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
 * Author: dowzyx
 * Create: 2022-06-02
 * Description: output of taskprobe
 ******************************************************************************/
#ifndef __OUTPUT_H__
#define __OUTPUT_H__

#ifdef BPF_PROG_KERN

#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "vmlinux.h"

#include "task.h"

#define BPF_F_INDEX_MASK    0xffffffffULL
#define BPF_F_CURRENT_CPU   BPF_F_INDEX_MASK

#define PERF_OUT_MAX (64)
struct bpf_map_def SEC("maps") output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = PERF_OUT_MAX,
};

// Data collection period
struct bpf_map_def SEC("maps") period_map = {
    .type = BPF_MAP_TYPE_ARRAY,
    .key_size = sizeof(u32),    // const value 0
    .value_size = sizeof(u64),  // period time as nanosecond
    .max_entries = 1,
};

#define PERIOD ((u64)30 * 1000000000)
static __always_inline u64 get_period()
{
    u32 key = 0;
    u64 period = PERIOD;

    u64 *value = (u64 *)bpf_map_lookup_elem(&period_map, &key);
    if (value)
        period = *value;

    return period; // units: nanosecond
}

static __always_inline __maybe_unused void report(void *ctx, struct task_data *val)
{
    u64 ts = bpf_ktime_get_ns();
    u64 period = get_period();
    if ((ts > val->ts) && ((ts - val->ts) < period)) {
        return;
    }
    val->ts = ts;
    (void)bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, val, sizeof(struct task_data));

    __builtin_memset(&(val->io), 0x0, sizeof(val->io));
}

#endif

#endif
