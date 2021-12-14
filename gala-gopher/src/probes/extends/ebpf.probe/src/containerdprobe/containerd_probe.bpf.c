// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2021 Huawei */

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif
#define BPF_PROG_USER
#include "bpf.h"
#include "containerd_probe.h"

char g_license[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") containers_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct container_key),
    .value_size = sizeof(struct container_value),
    .max_entries = CONTAINER_MAX_ENTRIES,
};

struct bpf_map_def SEC("maps") containerd_symaddrs_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(int),
    .value_size = sizeof(struct go_containerd_t),
    .max_entries = CONTAINER_MAX_ENTRIES,
};

UPROBE(linux_Task_Start, pt_regs)
{
    struct container_key key = {0};
    struct container_value value = {0};

    // containerd's info [pid + comm]
    value.containerd_pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&value.comm, sizeof(value.comm));
    
    // symbol's offset
    struct go_containerd_t *sym_str = bpf_map_lookup_elem(&containerd_symaddrs_map, &value.containerd_pid);
    if (!sym_str) {
        bpf_printk("=== Please Check containerd_symaddrs Update. \n");
        return;
    }
    
    // contained info [ID + ns + PID] from struct Task
    const void *sp = (const void *)PT_REGS_SP(ctx);
    void *t_ptr;
    bpf_probe_read(&t_ptr, sizeof(void *), sp + sym_str->task_Start_t_offset);
    bpf_probe_read(&value.task_pid, sizeof(int), t_ptr + sym_str->linux_Task_pid_offset);

    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&key.container_id, CONTAINER_ID_LEN * sizeof(char), id_str);

    void *ns_str;
    bpf_probe_read(&ns_str, sizeof(void *), t_ptr + sym_str->linux_Task_namespace_offset);
    bpf_probe_read_str(&value.namespace, NAMESPACE_LEN * sizeof(char), ns_str);

    value.status = 1;

    /* update hash map */
    bpf_map_update_elem(&containers_map, &key, &value, BPF_ANY);

    return;
}

UPROBE(linux_Task_Delete, pt_regs)
{
    struct container_key key = {0};
    struct container_value *v_str;

    // containerd's info
    unsigned int containerd_pid = bpf_get_current_pid_tgid() >> 32;
    
    // symbol's offset
    struct go_containerd_t *sym_str = bpf_map_lookup_elem(&containerd_symaddrs_map, &containerd_pid);
    if (!sym_str) {
        bpf_printk("=== Please Check containerd_symaddrs Update. \n");
        return;
    }
    
    // contained info [ID + ns + PID] from struct Task
    const void *sp = (const void *)PT_REGS_SP(ctx);
    void *t_ptr;
    bpf_probe_read(&t_ptr, sizeof(void *), sp + sym_str->task_Delete_t_offset);
    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&key.container_id, CONTAINER_ID_LEN * sizeof(char), id_str);

    /* lookup containerd map, update status */
    v_str = bpf_map_lookup_elem(&containers_map, &key);
    if (!v_str) {
        bpf_printk("===containerd Delete containerID not in hash map.\n");
        return;
    }

    v_str->status = 0;

    /* update hash map */
    bpf_map_update_elem(&containers_map, &key, v_str, BPF_ANY);

    return;
}