#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#include "killprobe.h"

char g_linsence[] SEC("license") = "GPL";


struct bpf_map_def SEC("maps") kill_info_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(struct val_t),
    .max_entries = KILL_INFO_MAX_NUM,
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

SEC("kprobe/__x64_sys_kill")
void sys_kill_probe(struct pt_regs *ctx)
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
        bpf_map_update_elem(&kill_info_map, &killer_pid, &val, BPF_ANY);
    }
}
