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
 * Create: 2022-06-10
 * Description: Collecting Task sched Data
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "task_map.h"
#include "output.h"


char g_linsence[] SEC("license") = "GPL";

static __always_inline void store_start(int pid, u32 cpu, u64 start)
{
    struct task_data *data;

    data = get_task(pid);
    if (data == NULL) {
        return;
    }

    data->cpu.off_cpu_start = start;
    return;
}

static __always_inline void store_end(void *ctx, int pid, u32 cpu, u64 end)
{
    u64 delta;
    struct task_data *data;

    data = get_task(pid);
    if (data == NULL) {
        return;
    }

    delta = (data->cpu.off_cpu_start < end) ? (end - data->cpu.off_cpu_start) : 0;
    if (delta > data->cpu.off_cpu_ns) {
        data->cpu.off_cpu_ns = delta;
        data->cpu.off_cpu_no = cpu;
        report(ctx, data);
    }
    return;
}

static __always_inline void update_migration(void *ctx, int pid, u32 cpu)
{
    struct task_data *data;
    data = get_task(pid);
    if (data == NULL) {
        return;
    }

    if (data->cpu.current_cpu_no == 0) {
        data->cpu.current_cpu_no = cpu;
        data->cpu.migration_count = 0;
        return;
    }

    if (data->cpu.current_cpu_no != cpu) {
        data->cpu.current_cpu_no = cpu;
        __sync_fetch_and_add(&data->cpu.migration_count, 1);
        report(ctx, data);
        return;
    }
}

KPROBE(finish_task_switch, pt_regs)
{
    struct task_struct* prev = (struct task_struct *)PT_REGS_PARM1(ctx);
    int prev_pid = _(prev->pid);

    int pid = (int)bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    u32 cpu = bpf_get_smp_processor_id();

    store_start(prev_pid, cpu, ts);
    store_end(ctx, pid, cpu, ts);

    update_migration(ctx, pid, cpu);
}


