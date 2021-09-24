// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2021 Huawei */
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "trace_haproxy.h"

char g_license[] SEC("license") = "Dual BSD/GPL";

#define _(P)                                            \
    ({                                                  \
        typeof(P) val;                                  \
        bpf_probe_read_user(&val, sizeof(val), &P);   \
        val;                                            \
    })

struct bpf_map_def SEC("maps") haproxy_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct link_key),
    .value_size = sizeof(struct link_value),
    .max_entries = LINK_MAX_ENTRIES,
};

static int sock_to_ip_str(struct ssockaddr_s *sock_addr, struct ip *ip_addr, unsigned short *port)
{
    struct sockaddr_in  *p;
    struct sockaddr_in6 *q;
    unsigned short family = _(sock_addr->ss_family);
    
    switch(family) {
        case AF_INET:
            p = (struct sockaddr_in *)sock_addr;
            ip_addr->ip4 = _(p->sin_addr);
            *port = _(p->sin_port);
            break;
        case AF_INET6:
            q = (struct sockaddr_in6 *)sock_addr;
            bpf_probe_read_user(&ip_addr->ip6, IP6_LEN, &q->sin6_addr);
            *port = _(q->sin_port);
            break;
        default:
            bpf_printk("=== ip_str family:%d abnormal.\n", family);
            break;
    }
    return family;
}

static int haproxy_obtain_key_value(struct stream_s *s, struct link_key *key)
{
    struct session      *sess_p;
    struct ha_listener  *l;
    struct receiver     rx_data = {0};
    struct connection_s *conn_p;
    struct ssockaddr_s  *sock_p;
    unsigned short  family;

    /* real server */
    sock_p = _(s->target_addr);
    family = sock_to_ip_str(sock_p, &key->s_addr, &key->s_port);

    /* C-H link */
    sess_p = _(s->sess);
    bpf_probe_read_user(&conn_p, sizeof(void *), &sess_p->origin);
    l = _(sess_p->listener);

	/* client value */
    sock_p = _(conn_p->src);
    (void)sock_to_ip_str(sock_p, &key->c_addr, &key->c_port);
    
	/* haproxy value */
    /* first, obtain info from listerner.rx.addr */
    bpf_probe_read_user(&rx_data, sizeof(struct receiver), (void *)&(l->rx));
    switch(family) {
		struct sockaddr_in  addr1;
        struct sockaddr_in6 addr2;
        case AF_INET:
            bpf_probe_read_user(&addr1, sizeof(struct sockaddr_in), (void *)&(rx_data.addr));
			key->p_addr.ip4 = addr1.sin_addr;
            key->p_port = addr1.sin_port;
            break;
        case AF_INET6:
            bpf_probe_read_user(&addr2, sizeof(struct sockaddr_in6), (void *)&(rx_data.addr));
			__builtin_memcpy(&key->p_addr.ip6, &addr2.sin6_addr, IP6_LEN - 1);
            key->p_port = addr2.sin_port;
            break;
        default:
            bpf_printk("=== obtain_key_value server family(%d) invalid.\n", family);
            break;
    }
	/* then, obtain info from connection.dst */
    sock_p = _(conn_p->dst);
    (void)sock_to_ip_str(sock_p, &key->p_addr, &key->p_port);

    return family;
}

SEC("uprobe/back_establish")
void haproxy_probe_estabilsh(struct pt_regs *ctx)
{
    struct stream_s     *p = (struct stream_s *)PT_REGS_PARM1(ctx);
    struct session      *sess_p;
    struct proxy        *proxy_p;
    struct link_key     key = {0};
    struct link_value   value = {0};

    /* process info */
    value.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&value.comm, sizeof(value.comm));

    /* c-p-s IP info */
    value.family = haproxy_obtain_key_value(p, &key);

    /* link type */
    sess_p = _(p->sess);
    proxy_p = _(sess_p->fe);
    value.type = _(proxy_p->mode);

    /* update link state */
    value.state = SI_ST_EST;

    /* update hash map */
    bpf_map_update_elem(&haproxy_link_map, &key, &value, BPF_ANY);

    return;
}

SEC("uprobe/stream_free")
void haproxy_probe_close(struct pt_regs *ctx)
{
    struct stream_s *p = (struct stream_s *)PT_REGS_PARM1(ctx);
    struct link_key key = {0};
    struct link_value   *value_p;

    /* ip info */
    (void)haproxy_obtain_key_value(p, &key);

    /* lookup hash map, update connect state */
    value_p = bpf_map_lookup_elem(&haproxy_link_map, &key);
    if (!value_p) {
        bpf_printk("===haproxy free stream not in hash map.\n");
        return;
    }
    /* update link state */
    value_p->state = SI_ST_CLO;

    /* update hash map */
    bpf_map_update_elem(&haproxy_link_map, &key, value_p, BPF_ANY);
    
    return;
}
