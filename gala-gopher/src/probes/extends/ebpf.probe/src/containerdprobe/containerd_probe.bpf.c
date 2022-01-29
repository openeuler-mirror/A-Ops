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
    unsigned int sym_key = SYMADDRS_MAP_KEY;

    // containerd's info [pid + comm]
    value.containerd_pid = bpf_get_current_pid_tgid() >> INT_LEN;
    bpf_get_current_comm(&value.comm, sizeof(value.comm));

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
    bpf_probe_read(&value.task_pid, sizeof(int), (void *)t_ptr + sym_str->linux_Task_pid_offset);

    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), (void *)t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&key.container_id, CONTAINER_ID_LEN * sizeof(char), id_str);

    void *ns_str;
    bpf_probe_read(&ns_str, sizeof(void *), (void *)t_ptr + sym_str->linux_Task_namespace_offset);
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
    unsigned int sym_key = SYMADDRS_MAP_KEY;

    // containerd's info
    unsigned int containerd_pid = bpf_get_current_pid_tgid() >> INT_LEN;

    // symbol's offset
    struct go_containerd_t *sym_str = bpf_map_lookup_elem(&containerd_symaddrs_map, &sym_key);
    if (sym_str == (void *)0) {
        bpf_printk("=== Please Check containerd_symaddrs Update. \n");
        return;
    }

    // contained info [ID + ns + PID] from struct Task
    const void *sp = (const void *)PT_REGS_SP(ctx);
    void *t_ptr;
    bpf_probe_read(&t_ptr, sizeof(void *), (void *)sp + sym_str->task_Delete_t_offset);
    void *id_str;
    bpf_probe_read(&id_str, sizeof(void *), (void *)t_ptr + sym_str->linux_Task_id_offset);
    bpf_probe_read_str(&key.container_id, CONTAINER_ID_LEN * sizeof(char), id_str);

    /* lookup containerd map, update status */
    v_str = bpf_map_lookup_elem(&containers_map, &key);
    if (!v_str == (void *)0) {
        bpf_printk("===containerd Delete containerID not in hash map.\n");
        return;
    }
    v_str->status = 0;

    /* update hash map */
    bpf_map_update_elem(&containers_map, &key, v_str, BPF_ANY);

    return;
}