/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 * Description: kill_probe bpf prog
 */
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "killprobe.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = 64,
};

struct bpf_map_def SEC("maps") monitor_killer_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = MONITOR_PIDS_MAX_NUM,
};

struct bpf_map_def SEC("maps") monitor_killed_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(pid_t),
    .value_size = sizeof(u32),
    .max_entries = MONITOR_PIDS_MAX_NUM,
};

KPROBE(__x64_sys_kill, pt_regs)
{
    pid_t killed_pid = (pid_t)PT_REGS_PARM1(ctx);
    int signal = (int)PT_REGS_PARM2(ctx);
    u32 killer_pid = bpf_get_current_pid_tgid();

    /* TODO: filter by monitor_killer_map */
    /* TODO: filter by monitor_killed_map */

    struct val_t val = {.killer_pid = killer_pid};
    if (bpf_get_current_comm(&val.comm, sizeof(val.comm)) == 0) {
        val.killed_pid = killed_pid;
        val.signal = signal;
        bpf_perf_event_output(ctx, &output, 0, &val, sizeof(val));
    }
}