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
 * Author: algorithmofdish
 * Create: 2021-10-25
 * Description: endpoint_probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include <bpf/bpf_endian.h>
#include "bpf.h"
#include "endpoint.h"

#define BIG_INDIAN_SK_FL_PROTO_SHIFT    16
#define BIG_INDIAN_SK_FL_PROTO_MASK     0x00ff0000
#define LITTLE_INDIAN_SK_FL_PROTO_SHIFT 8
#define LITTLE_INDIAN_SK_FL_PROTO_MASK  0x0000ff00
#define ETH_P_IP 0x0800
#define TCP_SOCK_REPAIR_MASK 0x02
#define rsk_listener    __req_common.skc_listener

#define ATOMIC_INC_EP_STATS(ep_val, metric) \
    __sync_fetch_and_add(&(ep_val)->ep_stats.stats[metric], 1)

char g_license[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") s_endpoint_map = {
    .type = BPF_MAP_TYPE_LRU_HASH,
    .key_size = sizeof(struct s_endpoint_key_t),
    .value_size = sizeof(struct endpoint_val_t),
    .max_entries = MAX_ENDPOINT_LEN,
};

struct bpf_map_def SEC("maps") c_endpoint_map = {
    .type = BPF_MAP_TYPE_LRU_HASH,
    .key_size = sizeof(struct c_endpoint_key_t),
    .value_size = sizeof(struct endpoint_val_t),
    .max_entries = MAX_ENDPOINT_LEN,
};

struct bpf_map_def SEC("maps") listen_port_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct listen_port_key_t),
    .value_size = sizeof(unsigned short),
    .max_entries = MAX_ENDPOINT_LEN,
};

struct bpf_map_def SEC("maps") listen_sockfd_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct listen_sockfd_key_t),
    .value_size = sizeof(int),
    .max_entries = MAX_ENDPOINT_LEN,
};

static __always_inline int is_little_endian()
{
    int i = 1;
    return (int)*((char *)&i) == 1;
}

#if KERNEL_VERSION(KER_VER_MAJOR, KER_VER_MINOR, KER_VER_PATCH) < KERNEL_VERSION(5, 6, 0)
static __always_inline int get_protocol(struct sock *sk)
{
    int protocol = 0;
    unsigned int sk_flags_offset = 0;

    bpf_probe_read(&sk_flags_offset, sizeof(unsigned int), sk->__sk_flags_offset);
    if (is_little_endian()) {
        protocol = (sk_flags_offset & LITTLE_INDIAN_SK_FL_PROTO_MASK) >> LITTLE_INDIAN_SK_FL_PROTO_SHIFT;
    } else {
        protocol = (sk_flags_offset & BIG_INDIAN_SK_FL_PROTO_MASK) >> BIG_INDIAN_SK_FL_PROTO_SHIFT;
    }

    return protocol;
}
#else
static __always_inline int get_protocol(struct sock *sk)
{
    int protocol = _(sk->sk_protocol);
    return protocol;
}
#endif

static __always_inline void init_listen_port_key(struct listen_port_key_t *listen_port_key, struct sock *sk)
{
    listen_port_key->tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    listen_port_key->protocol = get_protocol(sk);
    listen_port_key->port = _(sk->sk_num);

    return;
}

static __always_inline int is_listen_endpoint(struct sock *sk)
{
    struct listen_port_key_t listen_port_key = {0};
    void *val;

    init_listen_port_key(&listen_port_key, sk);
    val = bpf_map_lookup_elem(&listen_port_map, &listen_port_key);
    if (val != (void *)0) {
        return 1;
    }

    return 0;
}

static __always_inline struct sock *listen_sock(struct sock *sk)
{
    struct request_sock *req = (struct request_sock *)sk;
    struct sock *lsk = _(req->rsk_listener);

    return lsk;
}

static __always_inline void init_ip(struct ip *ip_addr, struct sock *sk)
{
    int family = _(sk->sk_family);
    if (family == AF_INET) {
        ip_addr->ip.ip4 = _(sk->sk_rcv_saddr);
    } else if (family == AF_INET6) {
        bpf_probe_read(ip_addr->ip.ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
    }
    ip_addr->family = family;

    return;
}

static __always_inline void init_listen_ep_key(struct s_endpoint_key_t *ep_key, struct sock *sk)
{
    ep_key->sock_p = (unsigned long)sk;
    return;
}

static __always_inline void init_client_ep_key(struct c_endpoint_key_t *ep_key, struct sock *sk)
{
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    ep_key->tgid = tgid;
    init_ip((struct ip *)&ep_key->ip_addr, sk);
    ep_key->protocol = get_protocol(sk);

    return;
}

static __always_inline void init_ep_val(struct endpoint_val_t *ep_val, struct sock *sk)
{
    struct socket *sock = _(sk->sk_socket);

    ep_val->uid = bpf_get_current_uid_gid();
    ep_val->tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    bpf_get_current_comm(&ep_val->comm, sizeof(ep_val->comm));
    ep_val->s_type = _(sock->type);
    ep_val->protocol = get_protocol(sk);
    init_ip((struct ip *)&ep_val->s_addr, sk);
    ep_val->s_port = _(sk->sk_num);

    return;
}

static __always_inline struct endpoint_val_t *get_listen_ep_val_by_sock(struct sock *sk)
{
    struct s_endpoint_key_t ep_key = {0};
    init_listen_ep_key(&ep_key, sk);

    return (struct endpoint_val_t*)bpf_map_lookup_elem(&s_endpoint_map, &ep_key);
}

static __always_inline struct endpoint_val_t *get_client_ep_val_by_sock(struct sock *sk)
{
    struct c_endpoint_key_t ep_key = {0};
    init_client_ep_key(&ep_key, sk);

    return (struct endpoint_val_t*)bpf_map_lookup_elem(&c_endpoint_map, &ep_key);
}

static __always_inline struct endpoint_val_t *get_ep_val_by_sock(struct sock *sk)
{
    struct sock *lsk;

    if (is_listen_endpoint(sk)) {
        lsk = listen_sock(sk);
        return get_listen_ep_val_by_sock(lsk);
    }

    return get_client_ep_val_by_sock(sk);
}

KPROBE_RET(inet_bind, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket *sock;
    struct probe_val val;

    struct sock *sk;
    int type;
    struct s_endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    struct listen_port_key_t listen_port_key = {0};
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    if (ret != 0) {
        return;
    }

    PROBE_GET_PARMS(inet_bind, ctx, val);
    sock = (struct socket *)PROBE_PARM1(val);
    sk = _(sock->sk);
    if (sk == (void *)0) {
        bpf_printk("====[tgid=%u]: sock is null.\n", tgid);
        return;
    }

    type = _(sock->type);
    if (type == SOCK_DGRAM) {
        init_listen_ep_key(&ep_key, sk);
        init_ep_val(&ep_val, sk);
        ep_val.type = SK_TYPE_LISTEN_UDP;
        err = bpf_map_update_elem(&s_endpoint_map, &ep_key, &ep_val, BPF_ANY);
        if (err < 0) {
            bpf_printk("====[tgid=%u]: new udp listen endpoint updates to map failed.\n", tgid);
            return;
        }
        bpf_printk("====[tgid=%u]: new udp listen endpoint created.\n", tgid);
        init_listen_port_key(&listen_port_key, sk);
        err = bpf_map_update_elem(&listen_port_map, &listen_port_key, &listen_port_key.port, BPF_ANY);
        if (err < 0) {
            bpf_printk("====[tgid=%u]: new udp listen port updates to map failed.\n", tgid);
        }
    }

    return;
}

KPROBE_RET(inet_listen, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket *sock;
    struct probe_val val;

    struct sock *sk;
    struct s_endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    struct listen_port_key_t listen_port_key = {0};
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    if (ret != 0) {
        return;
    }

    PROBE_GET_PARMS(inet_listen, ctx, val);
    sock = (struct socket *)PROBE_PARM1(val);
    sk = _(sock->sk);
    if (sk == (void *)0) {
        bpf_printk("====[tgid=%u]: sock is null.\n", tgid);
        return;
    }

    init_listen_ep_key(&ep_key, sk);
    init_ep_val(&ep_val, sk);
    ep_val.type = SK_TYPE_LISTEN_TCP;
    err = bpf_map_update_elem(&s_endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tgid=%u]: new tcp listen endpoint updates to map failed.\n", tgid);
        return;
    }
    bpf_printk("====[tgid=%u]: new tcp listen endpoint created.\n", tgid);
    init_listen_port_key(&listen_port_key, sk);
    err = bpf_map_update_elem(&listen_port_map, &listen_port_key, &listen_port_key.port, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tgid=%u]: new tcp listen port updates to map failed.\n", tgid);
    }

    return;
}

KPROBE(__sys_accept4, pt_regs)
{
    int fd = PT_REGS_PARM1(ctx);
    int *fd_ptr;
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    struct sock *sk;
    long err;

    struct listen_sockfd_key_t listen_sockfd_key = {0};
    struct s_endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};

    listen_sockfd_key.tgid = tgid;
    listen_sockfd_key.fd = fd;
    fd_ptr = (int *)bpf_map_lookup_elem(&listen_sockfd_map, &listen_sockfd_key);
    if (fd_ptr == (void *)0) {
        return;
    }

    if (task == (void *)0) {
        return;
    }
    sk = sock_get_by_fd(fd, task);
    if (sk == (void *)0) {
        return;
    }
    init_listen_ep_key(&ep_key, sk);
    init_ep_val(&ep_val, sk);
    ep_val.type = SK_TYPE_LISTEN_TCP;
    err = bpf_map_update_elem(&s_endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tgid=%u]: new tcp listen endpoint updates to map failed.\n", tgid);
        return;
    }
    bpf_printk("====[tgid=%u]: new tcp listen endpoint created.\n", tgid);
    bpf_map_delete_elem(&listen_sockfd_map, &listen_sockfd_key);

    return;
}

static __always_inline void _tcp_connect(struct pt_regs *ctx, struct sock *sk)
{
    int ret = PT_REGS_RC(ctx);
    struct c_endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    if (ret != 0) {
        return;
    }

    if (sk == (void *)0) {
        bpf_printk("====[tgid=%u]: sock is null.\n", tgid);
        return;
    }

    init_client_ep_key(&ep_key, sk);
    if (bpf_map_lookup_elem(&c_endpoint_map, &ep_key) != (void *)0) {
        return;
    }
    init_ep_val(&ep_val, sk);
    ep_val.s_port = 0;  /* reset s_port field for client endpoint */
    ep_val.type = SK_TYPE_CLIENT_TCP;
    ATOMIC_INC_EP_STATS(&ep_val, EP_STATS_ACTIVE_OPENS);
    err = bpf_map_update_elem(&c_endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tgid=%u]: new tcp client endpoint updates to map failed.\n", tgid);
        return;
    }
    bpf_printk("====[tgid=%u]: new tcp client endpoint created.\n", tgid);

    return;
}

KPROBE_RET(tcp_v4_connect, pt_regs)
{
    struct sock *sk;
    struct probe_val val;

    PROBE_GET_PARMS(tcp_v4_connect, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    _tcp_connect(ctx, sk);

    return;
}

KPROBE_RET(tcp_v6_connect, pt_regs)
{
    struct sock *sk;
    struct probe_val val;

    PROBE_GET_PARMS(tcp_v6_connect, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    _tcp_connect(ctx, sk);

    return;
}

KPROBE_RET(udp_sendmsg, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct c_endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    if (ret < 0) {
        return;
    }

    PROBE_GET_PARMS(udp_sendmsg, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        bpf_printk("====[tgid=%u]: sock is null.\n", tgid);
        return;
    }

    init_client_ep_key(&ep_key, sk);
    if (bpf_map_lookup_elem(&c_endpoint_map, &ep_key) != (void *)0) {
        return;
    }
    init_ep_val(&ep_val, sk);
    ep_val.s_port = 0;  /* reset s_port field for client endpoint */
    ep_val.type = SK_TYPE_CLIENT_UDP;
    err = bpf_map_update_elem(&c_endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tgid=%u]: new udp client endpoint updates to map failed.\n", tgid);
        return;
    }
    bpf_printk("====[tgid=%u]: new udp client endpoint created.\n", tgid);

    return;
}

KPROBE(__sock_release, pt_regs)
{
    struct socket *sock = (struct socket*)PT_REGS_PARM1(ctx);
    struct sock *sk = _(sock->sk);
    struct s_endpoint_key_t ep_key = {0};
    struct listen_port_key_t listen_port_key = {0};
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    init_listen_ep_key(&ep_key, sk);
    init_listen_port_key(&listen_port_key, sk);
    err = bpf_map_delete_elem(&s_endpoint_map, &ep_key);
    if (err == 0) {
        bpf_map_delete_elem(&listen_port_map, &listen_port_key);
        bpf_printk("====[tgid=%u]: endpoint has been removed.\n", tgid);
    }

    return;
}

static __always_inline void update_ep_listen_drop(struct endpoint_val_t *ep_val, struct sock *sk,
                                                  struct pt_regs *ctx)
{
    atomic_t sk_drops = _(sk->sk_drops);
    ep_val->ep_stats.stats[EP_STATS_LISTEN_DROPS] = sk_drops.counter;

    return;
}

static __always_inline bool sk_acceptq_is_full(const struct sock *sk)
{
    u32 ack_backlog = _(sk->sk_ack_backlog);
    u32 max_ack_backlog = _(sk->sk_max_ack_backlog);

    return ack_backlog > max_ack_backlog;
}

static __always_inline void update_ep_listen_overflow(struct endpoint_val_t *ep_val, struct sock *sk,
                                                      struct pt_regs *ctx)
{
    if (sk_acceptq_is_full(sk)) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_LISTEN_OVERFLOW);
    }

    return;
}

static __always_inline void update_ep_listen_overflow_v6(struct endpoint_val_t *ep_val, struct sock *sk,
                                                         struct pt_regs *ctx)
{
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM2(ctx);
    u16 protocol = _(skb->protocol);

    if (protocol == bpf_htons(ETH_P_IP)) {
        return;
    }

    if (sk_acceptq_is_full(sk)) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_LISTEN_OVERFLOW);
    }

    return;
}

static __always_inline void update_ep_requestfails(struct endpoint_val_t *ep_val, struct pt_regs *ctx)
{
    struct sock *ret = (struct sock *)PT_REGS_RC(ctx);
    if (ret == (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_REQUEST_FAILS);
    }

    return;
}

KPROBE(tcp_conn_request, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM3(ctx);
    struct endpoint_val_t *ep_val = get_listen_ep_val_by_sock(sk);

    if (ep_val != (void *)0) {
        update_ep_listen_drop(ep_val, sk, ctx);
        // here want_cookie may bypass listen overflow
        update_ep_listen_overflow(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_v4_syn_recv_sock, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val = get_listen_ep_val_by_sock(sk);

    if (ep_val != (void *)0) {
        update_ep_listen_drop(ep_val, sk, ctx);
        update_ep_listen_overflow(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_v6_syn_recv_sock, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val = get_listen_ep_val_by_sock(sk);

    if (ep_val != (void *)0) {
        update_ep_listen_drop(ep_val, sk, ctx);
        update_ep_listen_overflow_v6(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_req_err, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct sock *lsk = listen_sock(sk);
    struct endpoint_val_t *ep_val = get_listen_ep_val_by_sock(lsk);

    if (ep_val != (void *)0) {
        update_ep_listen_drop(ep_val, lsk, ctx);
    }

    return;
}

KPROBE_RET(tcp_create_openreq_child, pt_regs)
{
    struct sock *ret = (struct sock *)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct endpoint_val_t *ep_val;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if (ret == (void *)0) {
        return;
    }

    PROBE_GET_PARMS(tcp_create_openreq_child, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    ep_val = get_listen_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_PASSIVE_OPENS);
    }

    return;
}

KPROBE_RET(tcp_connect, pt_regs)
{
    int ret = (int)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct tcp_sock *tp;
    u8 repair_at;
    struct endpoint_val_t *ep_val;
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    long err;

    if (ret != 0) {
        return;
    }

    PROBE_GET_PARMS(tcp_connect, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    tp = (struct tcp_sock *)sk;
    err = bpf_probe_read(&repair_at, sizeof(u8), (void *)(((unsigned long)&tp->repair_queue) - 1));
    if (err < 0) {
        bpf_printk("====[tgid=%u]: read repair field of sock failed.\n", tgid);
        return;
    }
    if (repair_at & TCP_SOCK_REPAIR_MASK) {
        return;
    }

    ep_val = get_client_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_ACTIVE_OPENS);
    }

    return;
}

KPROBE(tcp_done, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    unsigned char state = _(sk->sk_state);
    struct endpoint_val_t *ep_val;

    if (state == TCP_SYN_SENT || state == TCP_SYN_RECV) {
        ep_val = get_ep_val_by_sock(sk);

        if (ep_val != (void *)0) {
            ATOMIC_INC_EP_STATS(ep_val, EP_STATS_ATTEMPT_FAILS);
        }
    }

    return;
}

KPROBE_RET(tcp_check_req, pt_regs)
{
    struct sock *sk;
    struct probe_val val;

    struct endpoint_val_t *ep_val;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    PROBE_GET_PARMS(tcp_check_req, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        update_ep_requestfails(ep_val, ctx);
    }

    return;
}

KPROBE(tcp_reset, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val;

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_ABORT_CLOSE);
    }

    return;
}

KPROBE_RET(tcp_try_rmem_schedule, pt_regs)
{
    int ret = (int)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct endpoint_val_t *ep_val;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if (ret == 0) {
        return;
    }

    PROBE_GET_PARMS(tcp_try_rmem_schedule, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_RMEM_SCHEDULE);
    }

    return;
}

KPROBE_RET(tcp_check_oom, pt_regs)
{
    bool ret = (bool)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct endpoint_val_t *ep_val;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if (!ret) {
        return;
    }

    PROBE_GET_PARMS(tcp_check_oom, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_TCP_OOM);
    }

    return;
}

KPROBE(tcp_write_wakeup, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    int mib = (int)PT_REGS_PARM2(ctx);
    struct endpoint_val_t *ep_val;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if (mib != LINUX_MIB_TCPKEEPALIVE) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val != (void *)0) {
        ATOMIC_INC_EP_STATS(ep_val, EP_STATS_KEEPLIVE_TIMEOUT);
    }

    return;
}

KPROBE_RET(init_conntrack, pt_regs)
{
    u32 pid __maybe_unused = bpf_get_current_pid_tgid() >> 32;
    return;
}

