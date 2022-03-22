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
 * Author: sky
 * Create: 2021-05-22
 * Description: tcp_probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include <bpf/bpf_endian.h>
#include "tcpprobe.h"

char g_linsence[] SEC("license") = "GPL";

#define __TCP_LINK_MAX (10 * 1024)
// Used to identifies the TCP link(including multiple establish tcp connection)
// and save TCP statistics.
struct bpf_map_def SEC("maps") tcp_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct tcp_link_s),
    .value_size = sizeof(struct tcp_metrics_s),
    .max_entries = __TCP_LINK_MAX,
};

#define __TCP_TUPLE_MAX (10 * 1024)
// Used to identifies the TCP sock object, and role of the SOCK object.
// Equivalent to TCP 5-tuple objects.
struct bpf_map_def SEC("maps") sock_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct sock *),
    .value_size = sizeof(u32),    // role: client:1/server:0
    .max_entries = __TCP_TUPLE_MAX,
};

struct bpf_map_def SEC("maps") output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = 64,
};

// Data collection period
struct bpf_map_def SEC("maps") period_map = {
    .type = BPF_MAP_TYPE_ARRAY,
    .key_size = sizeof(u32),    // const value 0
    .value_size = sizeof(u64),  // period time as second
    .max_entries = 1,
};

static __always_inline u32* get_sock_data(struct sock *sk)
{
    return (u32 *)bpf_map_lookup_elem(&sock_map, &sk);
}

static __always_inline int get_tcp_link_key(struct tcp_link_s *link, struct sock *sk, u32 tgid)
{
    if (!sk)
        return -1;

    u32 *role = get_sock_data(sk);
    if (!role) {
        return -1;
    }

    link->family = _(sk->sk_family);

    if (*role == LINK_ROLE_CLIENT) {
        if (link->family == AF_INET) {
            link->c_ip = _(sk->sk_rcv_saddr);
            link->s_ip = _(sk->sk_daddr);
        } else {
            bpf_probe_read_user(link->c_ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
            bpf_probe_read_user(link->s_ip6, IP6_LEN, &sk->sk_v6_daddr);
        }
        link->s_port = bpf_ntohs(_(sk->sk_dport));
    } else {
        if (link->family == AF_INET) {
            link->s_ip = _(sk->sk_rcv_saddr);
            link->c_ip = _(sk->sk_daddr);
        } else {
            bpf_probe_read_user(link->s_ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
            bpf_probe_read_user(link->c_ip6, IP6_LEN, &sk->sk_v6_daddr);
        }
        link->s_port = _(sk->sk_num);
    }

    link->role = *role;
    link->tgid = tgid;
    return 0;
}

static __always_inline int create_tcp_link(struct tcp_link_s *link) 
{
    struct tcp_metrics_s metrics = {0};

    metrics.ts = bpf_ktime_get_ns();
    __builtin_memcpy(&(metrics.link), link, sizeof(metrics.link));

    return bpf_map_update_elem(&tcp_link_map, link, &metrics, BPF_ANY);
}

static __always_inline struct tcp_metrics_s *get_tcp_metrics(struct sock *sk, u32 tgid, u32 *new_entry) 
{
    int ret;
    struct tcp_link_s link = {0};
    struct tcp_metrics_s *metrics;

    *new_entry = 0;
    ret = get_tcp_link_key(&link, sk, tgid);
    if (ret < 0)
        return 0;

    metrics = bpf_map_lookup_elem(&tcp_link_map, &link);
    if (metrics != (struct tcp_metrics_s *)0) {
        return metrics;
    }

    ret = create_tcp_link(&link);
    if (ret != 0)
        return 0;

    *new_entry = 1;
    return bpf_map_lookup_elem(&tcp_link_map, &link);
}

static __always_inline int create_sock_obj(u32 tgid, struct sock *sk, u32 role)
{
    if (!is_task_exist(tgid)) {
        return -1;
    }
    return bpf_map_update_elem(&sock_map, &sk, &role, BPF_ANY);
}

static __always_inline void delete_sock_obj(struct sock *sk)
{
    (void)bpf_map_delete_elem(&sock_map, &sk);
}

#define __PERIOD ((u64)30 * 1000000000)
static __always_inline u64 get_period()
{
    u32 key = 0;
    u64 period = __PERIOD;

    u64 *value = (u64 *)bpf_map_lookup_elem(&period_map, &key);
    if (value)
        period = *value;

    return period; // units from second to nanosecond
}

static __always_inline void report(struct pt_regs *ctx, struct tcp_metrics_s *metrics, u32 new_entry)
{
    if (new_entry) {
        (void)bpf_perf_event_output(ctx, &output, 0, metrics, sizeof(struct tcp_metrics_s));
    } else {
        u64 ts = bpf_ktime_get_ns();
        u64 period = get_period();
        if ((ts > metrics->ts) && ((ts - metrics->ts) < period)) {
            return;
        }
        metrics->ts = ts;
        (void)bpf_perf_event_output(ctx, &output, 0, metrics, sizeof(struct tcp_metrics_s));
    }

    __builtin_memset(&(metrics->data), 0x0, sizeof(metrics->data));
}

#define __TCP_FD_MAX (50)

// Used to identifies the TCP pid and fd.
// Temporary MAP. Data exists only in the startup phase.
struct bpf_map_def SEC("maps") tcp_fd_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),    // tgid
    .value_size = sizeof(struct tcp_fd_info),
    .max_entries = __TCP_FD_MAX,
};

static void do_load_tcp_fd(u32 tgid, int fd, int role)
{
    int ret;
    struct sock *sk;
    struct tcp_link_s link = {0};
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    if (fd == 0)
        return;

    sk = sock_get_by_fd(fd, task);
    if (sk == (struct sock *)0)
        return;

    ret = create_sock_obj(tgid, sk, role);
    if (ret < 0)
        return;

    ret = get_tcp_link_key(&link, sk, tgid);
    if (ret < 0)
        return;

    bpf_printk("load tcp fd(cip=%x, sip=%x).\n", link.c_ip, link.s_ip);
}

static void load_tcp_fd(u32 tgid)
{
    struct tcp_fd_info *tcp_fd_s = bpf_map_lookup_elem(&tcp_fd_map, &tgid);
    if (!tcp_fd_s)
        return;

#pragma clang loop unroll(full)
    for (int i = 0; i < TCP_FD_PER_PROC_MAX; i++) {
        do_load_tcp_fd(tgid, tcp_fd_s->fds[i], tcp_fd_s->fd_role[i]);
    }

    (void)bpf_map_delete_elem(&tcp_fd_map, &tgid);
}

// Creating a Sock Object of the Service Type
KRETPROBE(inet_csk_accept, pt_regs)
{
    int ret;
    struct sock *sk = (struct sock *)PT_REGS_RC(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;

    /* server: add new link */
    ret = create_sock_obj(tgid, sk, LINK_ROLE_SERVER);
    if (ret < 0)
        return;

    /* add long link sock map */
    load_tcp_fd(tgid);
    return;
}

KPROBE(tcp_set_state, pt_regs)
{
    int ret;
    u16 new_state = (u16)PT_REGS_PARM2(ctx);
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;

    if (new_state == TCP_SYN_SENT) {
        /* create sock object */
        ret = create_sock_obj(tgid, sk, LINK_ROLE_CLIENT);
        if (ret < 0)
            return;

        /* create tcp sock from tcp fd */
        load_tcp_fd(tgid);
    }
    return;
}

KRAWTRACE(tcp_destroy_sock, bpf_raw_tracepoint_args)
{
    struct sock *sk = (struct sock *)ctx->args[0];
    delete_sock_obj(sk);
}

KPROBE(tcp_sendmsg, pt_regs)
{
    u32 new_entry = 0;
    struct tcp_metrics_s *metrics;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    size_t size = (size_t)PT_REGS_PARM3(ctx);

    /* create tcp sock from tcp fd */
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    load_tcp_fd(tgid);

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_TX_XADD(metrics->data, size);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_recvmsg, pt_regs)
{
    u32 new_entry = 0;
    struct tcp_metrics_s *metrics;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);

    /* create tcp sock from tcp fd */
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    load_tcp_fd(tgid);

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_STATE_UPDATE(metrics->data, sk);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_drop, pt_regs)
{
    u32 new_entry = 0;
    struct tcp_metrics_s *metrics;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_SK_DROPS_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KPROBE_RET(tcp_add_backlog, pt_regs)
{
    u32 new_entry = 0;
    bool discard = (bool)PT_REGS_RC(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_add_backlog, ctx, val) < 0)
        return;

    if (discard) {
        sk = (struct sock *)PROBE_PARM1(val);

        metrics = get_tcp_metrics(sk, tgid, &new_entry);
        if (metrics) {
            TCP_BACKLOG_DROPS_INC(metrics->data);
            report(ctx, metrics, new_entry);
        }
    }
}

KPROBE_RET(tcp_v4_inbound_md5_hash, pt_regs)
{
    u32 new_entry = 0;
    bool discard = (bool)PT_REGS_RC(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_v4_inbound_md5_hash, ctx, val) < 0)
        return;

    if (discard) {

        sk = (struct sock *)PROBE_PARM1(val);

        metrics = get_tcp_metrics(sk, tgid, &new_entry);
        if (metrics) {
            TCP_MD5_DROPS_INC(metrics->data);
            report(ctx, metrics, new_entry);
        }
    }
}

KPROBE_RET(tcp_filter, pt_regs)
{
    u32 new_entry = 0;
    bool discard = (bool)PT_REGS_RC(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_filter, ctx, val) < 0)
        return;

    if (discard) {

        sk = (struct sock *)PROBE_PARM1(val);
        metrics = get_tcp_metrics(sk, tgid, &new_entry);
        if (metrics) {
            TCP_FILTER_DROPS_INC(metrics->data);
            report(ctx, metrics, new_entry);
        }
    }
}

KPROBE(tcp_write_err, pt_regs)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_TMOUT_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_cleanup_rbuf, pt_regs)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    int copied = (int)PT_REGS_PARM2(ctx);
    struct tcp_metrics_s *metrics;

    if (copied <= 0)
        return;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_RX_XADD(metrics->data, copied);
        report(ctx, metrics, new_entry);
    }
}

KRAWTRACE(sock_exceed_buf_limit, bpf_raw_tracepoint_args)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock*)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_SNDBUF_LIMIT_INC(metrics->data);
    }
}

KRAWTRACE(sock_rcvqueue_full, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock*)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_RCVQUE_FULL_INC(metrics->data);
    }
}

KRAWTRACE(tcp_send_reset, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_SEND_RSTS_INC(metrics->data);
    }
}

KRAWTRACE(tcp_receive_reset, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_RECEIVE_RSTS_INC(metrics->data);
    }
}

KRAWTRACE(tcp_retransmit_synack, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_RETRANS_INC(metrics->data);
    }
}

KRAWTRACE(tcp_retransmit_skb, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct tcp_metrics_s *metrics;

    metrics = get_tcp_metrics(sk, tgid, &new_entry);
    if (metrics) {
        TCP_RETRANS_INC(metrics->data);
    }
}

