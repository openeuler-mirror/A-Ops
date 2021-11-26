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

#define rsk_listener	__req_common.skc_listener

#define STORE_SOCK_ADDR(x) \
    do { \
        unsigned long addr = (unsigned long)PT_REGS_PARM##x(ctx); \
        add_item_to_sockmap(addr); \
    } while (0)

char LICENSE[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") endpoint_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct endpoint_key_t),
    .value_size = sizeof(struct endpoint_val_t),
    .max_entries = MAX_ENDPOINT_LEN,
};

struct bpf_map_def SEC("maps") sock_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(unsigned long),
    .max_entries = MAX_ENTRIES,
};

static __always_inline int is_little_endian()
{
    int i = 1;
    return (int)*((char *)&i) == 1;
}

static __always_inline struct sock *listen_sock(struct sock *sk)
{
    struct request_sock *req = (struct request_sock *)sk;
    struct sock *lsk = _(req->rsk_listener);
    return lsk;
}

static __always_inline void add_item_to_sockmap(unsigned long val)
{
    u32 tid = bpf_get_current_pid_tgid();
    bpf_map_update_elem(&sock_map, &tid, &val, BPF_ANY);
    return;
}

static __always_inline void *get_item_from_sockmap()
{
    u32 tid = bpf_get_current_pid_tgid();
    return bpf_map_lookup_elem(&sock_map, &tid);
}

static __always_inline struct sock *get_sock_from_sockmap()
{
    struct sock **skpp = (struct sock **)get_item_from_sockmap();
    if (!skpp) {
        return 0;
    }
    return *skpp;
}

static __always_inline void init_ep_key(struct endpoint_key_t *ep_key, unsigned long sock_p)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    ep_key->pid = pid;
    ep_key->sock_p = sock_p;
    return;
}

static __always_inline void init_ep_val(struct endpoint_val_t *ep_val, struct sock *sk)
{
    struct socket *sock = _(sk->sk_socket);
    unsigned int sk_flags_offset = 0;

    ep_val->type = SK_TYPE_INIT;
    ep_val->uid = bpf_get_current_uid_gid();
    bpf_get_current_comm(&ep_val->comm, sizeof(ep_val->comm));
    ep_val->s_type = _(sock->type);
    ep_val->family = _(sk->sk_family);
    bpf_probe_read(&sk_flags_offset, sizeof(unsigned int), sk->__sk_flags_offset);
    if (is_little_endian()) {
        ep_val->protocol = (sk_flags_offset & LITTLE_INDIAN_SK_FL_PROTO_MASK) >> LITTLE_INDIAN_SK_FL_PROTO_SHIFT;
    } else {
        ep_val->protocol = (sk_flags_offset & BIG_INDIAN_SK_FL_PROTO_MASK) >> BIG_INDIAN_SK_FL_PROTO_SHIFT;
    }
    
    return;
}

static __always_inline struct endpoint_val_t *get_ep_val_by_sock(struct sock *sk)
{
    struct endpoint_key_t ep_key = {0};
    init_ep_key(&ep_key, (unsigned long)sk);
    return (struct endpoint_val_t*)bpf_map_lookup_elem(&endpoint_map, &ep_key);
}

KPROBE(__sock_create, pt_regs)
{
    int type = (int)PT_REGS_PARM3(ctx);
    struct socket **res = (struct socket **)PT_REGS_PARM5(ctx);
    int kern = (int)PT_REGS_PARM6(ctx);
    u32 tid = bpf_get_current_pid_tgid();

    if (kern != 0) {
        return;
    }

    if (type != SOCK_STREAM && type != SOCK_DGRAM) {
        return;
    }

    add_item_to_sockmap((unsigned long)res);
    bpf_printk("====[tid=%u]: start creating new socket\n", tid);
    return;
}

KRETPROBE(__sock_create, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket ***sockppp;
    struct socket *sock;
    struct sock *sk;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    u32 tid = bpf_get_current_pid_tgid();
    long err;

    if (ret < 0) {
        goto cleanup;
    }

    sockppp = (struct socket ***)get_item_from_sockmap();
    if (!sockppp) {
        return;
    }
    sock = _(**sockppp);
    sk = _(sock->sk);
    if (!sk) {
        bpf_printk("====[tid=%u]: sock is null.\n", tid);
        goto cleanup;
    }

    init_ep_key(&ep_key, (unsigned long)sk);
    init_ep_val(&ep_val, sk);
    err = bpf_map_update_elem(&endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tid=%u]: new endpoint update to map failed\n", tid);
        goto cleanup;
    }
    bpf_printk("====[tid=%u]: new endpoint created.\n", tid);

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(inet_bind, pt_regs)
{
    bpf_printk("====[tid=%u]: start binding endpoint.\n", (u32)bpf_get_current_pid_tgid());
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(inet_bind, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket **sockpp;
    struct socket *sock;
    struct sock *sk;
    int type;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (ret != 0) {
        goto cleanup;
    }

    sockpp = (struct socket **)get_item_from_sockmap();
    if (!sockpp) {
        return;
    }
    sock = *sockpp;
    sk = _(sock->sk);
    if (!sk) {
        bpf_printk("====[tid=%u]: sock is null.\n", tid);
        goto cleanup;
    }

    init_ep_key(&ep_key, (unsigned long)sk);
    ep_val = (struct endpoint_val_t *)bpf_map_lookup_elem(&endpoint_map, &ep_key);
    if (!ep_val) {
        bpf_printk("====[tid=%u]: endpoint can not find.\n", tid);
        goto cleanup;
    }

    struct ip *ip_addr = (struct ip*)&(ep_val->s_addr);
    if (ep_val->family == AF_INET) {
        ip_addr->ip4 = _(sk->sk_rcv_saddr);
    } else if (ep_val->family == AF_INET6) {
        bpf_probe_read(ip_addr->ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
    }
    ep_val->s_port = _(sk->sk_num);

    type = _(sock->type);
    if (type == SOCK_DGRAM) {
        ep_val->type = SK_TYPE_LISTEN_UDP;
        bpf_printk("====[tid=%u]: endpoint has been set to udp listening state.\n", tid);
    }
    
cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(inet_listen, pt_regs)
{
    bpf_printk("====[tid=%u]: start listening endpoint.\n", (u32)bpf_get_current_pid_tgid());
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(inet_listen, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket **sockpp;
    struct socket *sock;
    struct sock *sk;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();
    long err;

    if (ret != 0) {
        goto cleanup;
    }

    sockpp = (struct socket **)get_item_from_sockmap();
    if (!sockpp) {
        return;
    }
    sock = *sockpp;
    sk = _(sock->sk);
    if (!sk) {
        bpf_printk("====[tid=%u]: sock is null.\n", tid);
        goto cleanup;
    }

    init_ep_key(&ep_key, (unsigned long)sk);
    ep_val = (struct endpoint_val_t *)bpf_map_lookup_elem(&endpoint_map, &ep_key);
    if (ep_val) {
        ep_val->type = SK_TYPE_LISTEN_TCP;
        bpf_printk("====[tid=%u]: endpoint has been set to tcp listening state.\n", tid);
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(__sock_release, pt_regs)
{
    struct socket *sock = (struct socket*)PT_REGS_PARM1(ctx);
    struct sock *sk = _(sock->sk);
    struct endpoint_key_t ep_key = {0};
    u32 tid = bpf_get_current_pid_tgid();
    long err;
    init_ep_key(&ep_key, (unsigned long)sk);
    err = bpf_map_delete_elem(&endpoint_map, &ep_key);
    if (!err) {
        bpf_printk("====[tid=%u]: endpoint has been removed.\n", tid);
    }
    return;
}

static __always_inline void update_ep_listen_drop(struct endpoint_val_t *ep_val, struct sock *sk, struct pt_regs *ctx)
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

static __always_inline void update_ep_listen_overflow(struct endpoint_val_t *ep_val, struct sock *sk, struct pt_regs *ctx)
{
    if (sk_acceptq_is_full(sk)) {
        (ep_val->ep_stats.stats[EP_STATS_LISTEN_OVERFLOW])++;
    }
    return;
}

static __always_inline void update_ep_listen_overflow_v6(struct endpoint_val_t *ep_val, struct sock *sk, struct pt_regs *ctx)
{
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM2(ctx);
    u16 protocol = _(skb->protocol);

    if (protocol == bpf_htons(ETH_P_IP)) {
        return;
    }

    if (sk_acceptq_is_full(sk)) {
        (ep_val->ep_stats.stats[EP_STATS_LISTEN_OVERFLOW])++;
    }
    return;
}

static __always_inline void update_ep_requestfails(struct endpoint_val_t *ep_val, struct pt_regs *ctx)
{
    struct sock *ret = (struct sock *)PT_REGS_RC(ctx);
    if (!ret) {
        (ep_val->ep_stats.stats[EP_STATS_REQUEST_FAILS])++;
    }
    return;
}

KPROBE(tcp_conn_request, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM3(ctx);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(sk);

    if (ep_val) {
        update_ep_listen_drop(ep_val, sk, ctx);
        // here want_cookie may bypass listen overflow
        update_ep_listen_overflow(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_v4_syn_recv_sock, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(sk);

    if (ep_val) {
        update_ep_listen_drop(ep_val, sk, ctx);
        update_ep_listen_overflow(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_v6_syn_recv_sock, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(sk);

    if (ep_val) {
        update_ep_listen_drop(ep_val, sk, ctx);
        update_ep_listen_overflow_v6(ep_val, sk, ctx);
    }

    return;
}

KPROBE(tcp_req_err, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct sock *lsk = listen_sock(sk);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(lsk);

    if (ep_val) {
        update_ep_listen_drop(ep_val, lsk, ctx);
    }

    return;
}

KPROBE(tcp_create_openreq_child, pt_regs)
{
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(tcp_create_openreq_child, pt_regs)
{
    struct sock *ret = (struct sock *)PT_REGS_RC(ctx);
    struct sock *sk;
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (!ret) {
        goto cleanup;
    }

    sk = get_sock_from_sockmap();
    if (!sk) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_PASSIVE_OPENS])++;
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(tcp_connect, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct tcp_sock *tp = (struct tcp_sock *)sk;
    u32 tid = bpf_get_current_pid_tgid();
    u8 repair_at;
    long err;

    err = bpf_probe_read(&repair_at, sizeof(u8), (void *)(((unsigned long)&tp->repair_queue) - 1));
    if (err < 0) {
        bpf_printk("====[tid=%u]: read repair field of sock failed.\n", tid);
        return;
    }
    if (repair_at & TCP_SOCK_REPAIR_MASK) {
        return;
    }

    add_item_to_sockmap((unsigned long)sk);
    return;
}

KRETPROBE(tcp_connect, pt_regs)
{
    int ret = (int)PT_REGS_RC(ctx);
    struct sock *sk;
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (ret != 0) {
        goto cleanup;
    }

    sk = get_sock_from_sockmap();
    if (!sk) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_ACTIVE_OPENS])++;
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(tcp_done, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    unsigned char state = _(sk->sk_state);
    struct endpoint_val_t *ep_val;

    if (state == TCP_SYN_SENT || state == TCP_SYN_RECV) {
        if (state == TCP_SYN_RECV) {
            sk = listen_sock(sk);
        }

        ep_val = get_ep_val_by_sock(sk);
        if (ep_val) {
            (ep_val->ep_stats.stats[EP_STATS_ATTEMPT_FAILS])++;
        }
    }

    return;
}

KPROBE(tcp_check_req, pt_regs)
{
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(tcp_check_req, pt_regs)
{
    struct sock *sk;
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    sk = get_sock_from_sockmap();
    if (!sk) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val) {
        update_ep_requestfails(ep_val, ctx);
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

static __always_inline void update_ep_abortclose(struct endpoint_val_t *ep_val, struct sock *sk)
{
    unsigned char state = _(sk->sk_state);

    if (state == TCP_SYN_SENT) {
        (ep_val->ep_stats.stats[EP_STATS_ABORT_CLOSE])++;
    }

    return;
}

KPROBE(tcp_reset, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(sk);

    if (ep_val) {
        update_ep_abortclose(ep_val, sk);
    }
    
    return;
}

KPROBE(tcp_try_rmem_schedule, pt_regs)
{
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(tcp_try_rmem_schedule, pt_regs)
{
    int ret = (int)PT_REGS_RC(ctx);
    struct sock *sk;
    struct sock *lsk;
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (ret == 0) {
        goto cleanup;
    }

    sk = get_sock_from_sockmap();
    if (!sk) {
        return;
    }

    lsk = listen_sock(sk);
    ep_val = get_ep_val_by_sock(lsk);
    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_RMEM_SCHEDULE])++;
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(tcp_check_oom, pt_regs)
{
    STORE_SOCK_ADDR(1);
    return;
}

KRETPROBE(tcp_check_oom, pt_regs)
{
    bool ret = (bool)PT_REGS_RC(ctx);
    struct sock *sk;
    struct sock *lsk;
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (!ret) {
        goto cleanup;
    }

    sk = get_sock_from_sockmap();
    if (!sk) {
        return;
    }

    lsk = listen_sock(sk);
    ep_val = get_ep_val_by_sock(lsk);
    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_TCP_OOM])++;
    }

cleanup:
    bpf_map_delete_elem(&sock_map, &tid);
    return;
}

KPROBE(tcp_send_active_reset, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct sock *lsk = listen_sock(sk);
    struct endpoint_val_t *ep_val = get_ep_val_by_sock(lsk);

    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_SEND_TCP_RSTS])++;
    }
    
    return;
}

KPROBE(tcp_write_wakeup, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    int mib = (int)PT_REGS_PARM2(ctx);
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (mib != LINUX_MIB_TCPKEEPALIVE) {
        return;
    }

    ep_val = get_ep_val_by_sock(sk);
    if (ep_val) {
        (ep_val->ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT])++;
    }

    return;
}