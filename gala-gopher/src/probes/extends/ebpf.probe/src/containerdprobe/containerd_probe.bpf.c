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
 * Author: dowzyx
 * Create: 2021-12-04
 * Description: container probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif
#define BPF_PROG_USER
#include "bpf.h"
#include "containerd_probe.h"

char g_license[] SEC("license") = "GPL";


struct bpf_map_def SEC("maps") output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(__u32),
    .value_size = sizeof(__u32),
    .max_entries = 64,
};

struct bpf_map_def SEC("maps") containerd_symaddrs_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(int),
    .value_size = sizeof(struct go_containerd_t),
    .max_entries = CONTAINER_MAX_ENTRIES,
};

static __always_inline void report(void *ctx, struct container_evt_s *evt)
{
    (void)bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, evt, sizeof(struct container_evt_s));
}

UPROBE(linux_Task_Start, pt_regs)
{
    struct container_evt_s evt = {0};
    unsigned int sym_key = SYMADDRS_MAP_KEY;

    // containerd's info [pid + comm]
    evt.tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));

    // symbol's offset
    struct go_containerd_t *sym_str = bpf_map_lookup_elem(&containerd_symaddrs_map, &sym_key);
    if (sym_str == (void *)0) {
        bpf_printk("=== Please Check containerd_symaddrs Update. \n");
        return;
    }

    // contained info [ID + ns + PID] from struct Task
    const void *sp = (const void *)PT_REGS_SP(ctx);
    void *t_ptr;
    bpf_probe_read(&t_ptr, sizeof(void *), (void *)sp + sym_str->task_Start_t_offset);
    bpf_probe_read(&evt.task_pid, sizeof(int), (char *)t_ptr + sym_str->linux_Task_pid_offset);

    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), (char *)t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&evt.k.container_id, (CONTAINER_ID_LEN + 1) * sizeof(char), id_str);

    void *ns_str;
    bpf_probe_read(&ns_str, sizeof(void *), (char *)t_ptr + sym_str->linux_Task_namespace_offset);
    bpf_probe_read_str(&evt.namespace, (NAMESPACE_LEN + 1) * sizeof(char), ns_str);

    report(ctx, &evt);
    return;
}

UPROBE(linux_Task_Delete, pt_regs)
{
    struct container_evt_s evt = {0};
    unsigned int sym_key = SYMADDRS_MAP_KEY;

    evt.crt_or_del = 1;     // delete event
    // symbol's offset
    struct go_containerd_t *sym_str = bpf_map_lookup_elem(&containerd_symaddrs_map, &sym_key);
    if (sym_str == (void *)0) {
        bpf_printk("=== Please Check containerd_symaddrs Update. \n");
        return;
    }

    // contained info [ID + ns + PID] from struct Task
    const void *sp = (const void *)PT_REGS_SP(ctx);
    void *t_ptr;
    bpf_probe_read(&t_ptr, sizeof(void *), (char *)sp + sym_str->task_Delete_t_offset);
    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), (char *)t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&evt.k.container_id, (CONTAINER_ID_LEN + 1) * sizeof(char), id_str);

    report(ctx, &evt);

    return;
}
