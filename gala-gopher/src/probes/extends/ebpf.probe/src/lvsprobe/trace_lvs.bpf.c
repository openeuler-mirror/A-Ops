// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2021 Huawei */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "trace_lvs.h"

#if defined(__TARGET_ARCH_x86)
#define PT_REGS_PARM6(x) ((x)->r9)
#elif defined(__TARGET_ARCH_arm64)
#define PT_REGS_ARM64 const volatile struct user_pt_regs
#define PT_REGS_PARM6(x) (((PT_REGS_ARM64 *)(x))->regs[5])
#endif

char g_linsence[] SEC("license") = "GPL";

#define _(P)                                            \
    ({                                                  \
        typeof(P) val;                                  \
        bpf_probe_read_kernel(&val, sizeof(val), &P);   \
        val;                                            \
    })

struct bpf_map_def SEC("maps") lvs_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct link_key),
    .value_size = sizeof(struct link_value),
    .max_entries = IPVS_MAX_ENTRIES,
};

struct bpf_map_def SEC("maps") lvs_flag_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u16),
    .value_size = sizeof(u8),
    .max_entries = IPVS_MIN_ENTRIES,
};

static void ipvs_state_get_key(struct ip_vs_conn *p, struct link_key *key, struct ip *addr, u16 *port)
{
    key->family = _(p->af);
    switch(key->family) {
        case AF_INET:
            /* server */
            bpf_probe_read_kernel(&key->s_addr.in, sizeof(struct in_addr), &p->daddr);
            /* client */
            bpf_probe_read_kernel(&key->c_addr.in, sizeof(struct in_addr), &p->caddr);
            /* virtural */
            bpf_probe_read_kernel(&key->v_addr.in, sizeof(struct in_addr), &p->vaddr);
            break;
        case AF_INET6:
            bpf_probe_read_kernel(&key->s_addr.in6, sizeof(struct in6_addr), &p->daddr);
            /* client */
            bpf_probe_read_kernel(&key->c_addr.in6, sizeof(struct in6_addr), &p->caddr);
            /* virtural */
            bpf_probe_read_kernel(&key->v_addr.in6, sizeof(struct in6_addr), &p->vaddr);
            break;
        default:
            bpf_printk("===LVS probe get tcp af invalid. \n");
            break;
    }
    key->s_port = _(p->dport);
    key->c_port = _(p->cport);
    key->v_port = _(p->vport);
    *addr = key->v_addr;
    *port = key->v_port;

    return;
}

static void ipvs_fnat_state_get_key(struct ip_vs_conn_fnat *p, struct link_key *key, struct ip *addr, u16 *port)
{
    key->family = _(p->af);
    switch(key->family) {
        case AF_INET:
            /* server */
            bpf_probe_read_kernel(&key->s_addr.in, sizeof(struct in_addr), &p->daddr);
            /* local */
            bpf_probe_read_kernel(&addr->in, sizeof(struct in_addr), &p->laddr);
            /* client */
            bpf_probe_read_kernel(&key->c_addr.in, sizeof(struct in_addr), &p->caddr);
            /* virtural */
            bpf_probe_read_kernel(&key->v_addr.in, sizeof(struct in_addr), &p->vaddr);
            break;
        case AF_INET6:
            /* server */
            bpf_probe_read_kernel(&key->s_addr.in6, sizeof(struct in6_addr), &p->daddr);
            /* local */
            bpf_probe_read_kernel(&addr->in6, sizeof(struct in6_addr), &p->laddr);
            /* client */
            bpf_probe_read_kernel(&key->c_addr.in6, sizeof(struct in6_addr), &p->caddr);
            /* virtural */
            bpf_probe_read_kernel(&key->v_addr.in6, sizeof(struct in6_addr), &p->vaddr);
            break;
        default:
            bpf_printk("===LVS probe get tcp af invalid. \n");
            break;
    }
    key->s_port = _(p->dport);
    key->c_port = _(p->cport);
    key->v_port = _(p->vport);
    *port = _(p->lport);

    return;
}

SEC("kprobe/ip_vs_conn_new")
void ipvs_conn_probe(struct pt_regs *ctx)
{
    u16 f_key = IPVS_FLAGS_KEY_VAL;

    /* obtain ipvs flags */
    u32 flags = (unsigned int)PT_REGS_PARM5(ctx);
    struct ip_vs_dest *dest = (struct ip_vs_dest *)PT_REGS_PARM6(ctx);
    atomic_t conn_flags = _(dest->conn_flags);
    flags |= conn_flags.counter;
    flags = flags & IP_VS_CONN_F_FWD_MASK;

    /* update hash map */
    bpf_map_update_elem(&lvs_flag_map, &f_key, &flags, BPF_ANY);

    return;
}

SEC("kretprobe/ip_vs_conn_new")
void ipvs_conn_new_probe(struct pt_regs *ctx)
{
    u16 f_key = IPVS_FLAGS_KEY_VAL;
    char flags = IP_VS_CONN_F_LOCALNODE;
    struct link_key     key = {0};
    struct link_value   value = {0};

    /* lookup ipvs flags */
    char *buf = bpf_map_lookup_elem(&lvs_flag_map, &f_key);
    if (buf) {
        flags = *buf;
    }
    bpf_printk("===LVS new_ret get flags[0x%x]. \n", flags);

    /* obtain key data */
    if (flags < IP_VS_CONN_FULLNAT) {
        struct ip_vs_conn *conn_p = (struct ip_vs_conn *)PT_REGS_RC(ctx);
        ipvs_state_get_key(conn_p, &key, &value.l_addr, &value.l_port);
    } else {
        struct ip_vs_conn_fnat *conn_p = (struct ip_vs_conn_fnat *)PT_REGS_RC(ctx);
        ipvs_fnat_state_get_key(conn_p, &key, &value.l_addr, &value.l_port);
    }

    /* update hash map */
    bpf_map_update_elem(&lvs_link_map, &key, &value, BPF_ANY);

    return;
}

SEC("kprobe/ip_vs_conn_expire")
void ipvs_conn_expire_probe(struct pt_regs *ctx)
{
    struct ip_vs_conn_fnat  *ip_vs_fnat_conn_p;
    struct ip_vs_conn       *ip_vs_conn_p;
    u16  f_key = IPVS_FLAGS_KEY_VAL;
    char flags = IP_VS_CONN_F_LOCALNODE;
    struct link_key     key = {0};
    struct link_value   *value_p;
    struct ip           local_addr = {0};
    u16                 local_port = 0;
    struct timer_list   *t = (struct timer_list *)PT_REGS_PARM1(ctx);

    /* lookup ipvs flags */
    char *buf = bpf_map_lookup_elem(&lvs_flag_map, &f_key);
    if (buf) {
        flags = *buf;
    }

    /* obtain struct ip_vs_conn's head addr */
    if (flags < IP_VS_CONN_FULLNAT) {
        ip_vs_conn_p = container_of(t, struct ip_vs_conn, timer);
    } else {
        ip_vs_fnat_conn_p = container_of(t, struct ip_vs_conn_fnat, timer);
    }

    /* obtain key data */
    if (flags < IP_VS_CONN_FULLNAT) {
        ipvs_state_get_key(ip_vs_conn_p, &key, &local_addr, &local_port);
    } else {
        ipvs_fnat_state_get_key(ip_vs_fnat_conn_p, &key, &local_addr, &local_port);
    }

    /* lookup hash map, update connect state */
    value_p = bpf_map_lookup_elem(&lvs_link_map, &key);
    if (!value_p) {
        bpf_printk("===LVS ubind dest not in hash map.\n");
        return;
    }
    value_p->state = IP_VS_TCP_S_CLOSE;
    value_p->close_ts = bpf_ktime_get_ns();
    value_p->l_addr = local_addr;
    value_p->l_port = local_port;
    
    bpf_map_update_elem(&lvs_link_map, &key, value_p, BPF_ANY);

    return;
}
