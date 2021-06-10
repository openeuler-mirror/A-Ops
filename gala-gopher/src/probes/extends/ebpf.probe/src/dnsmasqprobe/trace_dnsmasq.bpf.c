// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2021 Huawei */
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "trace_dnsmasq.h"

#if defined(__TARGET_ARCH_x86)
#define PT_REGS_PARM6(x) ((x)->r9)
#elif defined(__TARGET_ARCH_arm64)
#define PT_REGS_ARM64 const volatile struct user_pt_regs
#define PT_REGS_PARM6(x) (((PT_REGS_ARM64 *)(x))->regs[5])
#endif

char g_license[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") dns_query_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct link_key),
    .value_size = sizeof(struct link_value),
    .max_entries = LINK_MAX_ENTRIES,
};

SEC("uprobe/send_from")
void dnsmasq_probe_send_from(struct pt_regs *ctx)
{
    union mysockaddr    *to_p;
    union all_addr      *source_p;
    struct link_key     key = {0};
    struct link_value   value = {0};

    to_p = (union mysockaddr *)PT_REGS_PARM5(ctx);
    source_p = (union all_addr *)PT_REGS_PARM6(ctx);
    
    /* ip address */
    bpf_probe_read_user(&key.family, sizeof(short), &to_p->sa.sa_family);
    switch (key.family) {
        case AF_INET:
            bpf_probe_read_user(&key.c_addr.ip4, sizeof(int), &to_p->in.sin4_addr);
            bpf_probe_read_user(&key.c_port, sizeof(short), &to_p->in.sin_port);
            bpf_probe_read_user(&key.dns_addr.ip4, sizeof(int), &source_p->addr4);
            // bpf_printk("=== caddr[0x%x : %d] dns[0x%x].\n", key.c_addr.ip4, key.c_port, key.dns_addr.ip4);
            break;
        case AF_INET6:
            bpf_probe_read_user(&key.c_addr.ip6, IP6_LEN, &to_p->in6.sin6_addr);
            bpf_probe_read_user(&key.c_port, sizeof(short), &to_p->in6.sin_port);
            bpf_probe_read_user(&key.dns_addr.ip6, IP6_LEN, &source_p->addr6);
            break;
        default:
            bpf_printk("=== ip_str family:%d abnormal.\n", key.family);
            break;
    }
    
    /* link_value process info*/
    value.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&value.comm, sizeof(value.comm));
    
    /* update hash map */
    bpf_map_update_elem(&dns_query_link_map, &key, &value, BPF_ANY);

    return;
}