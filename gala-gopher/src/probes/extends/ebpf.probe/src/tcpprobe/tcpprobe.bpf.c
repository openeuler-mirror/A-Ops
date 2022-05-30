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
    .value_size = sizeof(struct tcp_sock_info),
    .max_entries = __TCP_TUPLE_MAX,
};

struct bpf_map_def SEC("maps") output = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
    .max_entries = 64,
};

// args
struct bpf_map_def SEC("maps") args_map = {
    .type = BPF_MAP_TYPE_ARRAY,
    .key_size = sizeof(u32),    // const value 0
    .value_size = sizeof(struct tcp_args_s),  // tcp probe args
    .max_entries = 1,
};

static __always_inline struct tcp_sock_info *get_sock_data(struct sock *sk)
{
    return (struct tcp_sock_info *)bpf_map_lookup_elem(&sock_map, &sk);
}

static __always_inline u16 get_cport_flag()
{
    u32 key = 0;
    u16 cport_flag = 0; // default: invalid
    struct tcp_args_s *args;

    args = (struct tcp_args_s *)bpf_map_lookup_elem(&args_map, &key);
    if (args)
        cport_flag = (u16)args->cport_flag;

    return cport_flag;
}

static __always_inline char is_valid_tgid(u32 tgid)
{
    u32 key = 0;
    struct tcp_args_s *args;

    args = (struct tcp_args_s *)bpf_map_lookup_elem(&args_map, &key);
    if (args && args->filter_by_task) {
        return is_task_exist((int)tgid);
    }

    if (args && args->filter_by_tgid) {
        return (args->filter_by_tgid == tgid);
    }

    return 1;
}

static __always_inline int get_tcp_link_key(struct tcp_link_s *link, struct sock *sk, u32 *syn_srtt)
{
    if (!sk)
        return -1;

    struct tcp_sock_info *sock_data_p = get_sock_data(sk);
    if (!sock_data_p || sock_data_p->tgid == 0) {
        return -1;
    }
    __u32 role = sock_data_p->role;
    *syn_srtt = sock_data_p->syn_srtt;

    /* update c_port_flag */
    link->c_flag = get_cport_flag();

    link->family = _(sk->sk_family);

    if (role == LINK_ROLE_CLIENT) {
        if (link->family == AF_INET) {
            link->c_ip = _(sk->sk_rcv_saddr);
            link->s_ip = _(sk->sk_daddr);
        } else {
            bpf_probe_read_user(link->c_ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
            bpf_probe_read_user(link->s_ip6, IP6_LEN, &sk->sk_v6_daddr);
        }
        link->s_port = bpf_ntohs(_(sk->sk_dport));
        if (link->c_flag == 1) {
            link->c_port = bpf_ntohs(_(sk->sk_num));
        } else {
            link->c_port = 0;
        }
    } else {
        if (link->family == AF_INET) {
            link->s_ip = _(sk->sk_rcv_saddr);
            link->c_ip = _(sk->sk_daddr);
        } else {
            bpf_probe_read_user(link->s_ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
            bpf_probe_read_user(link->c_ip6, IP6_LEN, &sk->sk_v6_daddr);
        }
        link->s_port = _(sk->sk_num);
        if (link->c_flag == 1) {
            link->c_port = bpf_ntohs(_(sk->sk_dport));
        } else {
            link->c_port = 0;
        }
    }

    link->role = role;
    link->tgid = sock_data_p->tgid;
    return 0;
}

static __always_inline int create_tcp_link(struct tcp_link_s *link, u32 syn_srtt)
{
    struct tcp_metrics_s metrics = {0};

    metrics.ts = bpf_ktime_get_ns();
    metrics.data.syn_status.syn_srtt_last = syn_srtt;
    __builtin_memcpy(&(metrics.link), link, sizeof(metrics.link));

    return bpf_map_update_elem(&tcp_link_map, link, &metrics, BPF_ANY);
}

static __always_inline int delete_tcp_link(struct sock *sk)
{
    struct tcp_link_s link = {0};
    u32 syn_srtt __maybe_unused = 0;

    if (link.c_flag == 0) {
        /* if cport_flag is invalid, return */
        return 0;
    }

    if (get_tcp_link_key(&link, sk, &syn_srtt) < 0) {
        bpf_printk("delete link map fail, because get key fail.\n");
        return -1;
    }

    return bpf_map_delete_elem(&tcp_link_map, &link);
}

static __always_inline struct tcp_metrics_s *get_tcp_metrics(struct sock *sk, u32 *new_entry) 
{
    int ret;
    struct tcp_link_s link = {0};
    struct tcp_metrics_s *metrics;
    u32 syn_srtt;

    *new_entry = 0;
    ret = get_tcp_link_key(&link, sk, &syn_srtt);
    if (ret < 0)
        return 0;

    metrics = bpf_map_lookup_elem(&tcp_link_map, &link);
    if (metrics != (struct tcp_metrics_s *)0) {
        if (link.role == LINK_ROLE_SERVER) {
            metrics->data.syn_status.syn_srtt_last = syn_srtt;
        }
        return metrics;
    }

    ret = create_tcp_link(&link, syn_srtt);
    if (ret != 0)
        return 0;

    *new_entry = 1;
    return bpf_map_lookup_elem(&tcp_link_map, &link);
}

static __always_inline int create_sock_obj(u32 tgid, struct sock *sk, struct tcp_sock_info *info)
{
    if (!is_valid_tgid(tgid))
        return -1;

    info->tgid = tgid;
    return bpf_map_update_elem(&sock_map, &sk, info, BPF_ANY);
}

static __always_inline void delete_sock_obj(struct sock *sk)
{
    (void)bpf_map_delete_elem(&sock_map, &sk);
}

static __always_inline void update_sock_obj(struct sock *sk, u32 tgid)
{
    struct tcp_sock_info * sk_info = get_sock_data(sk);
    if (sk_info == 0)
        return;
    sk_info->tgid = tgid;
    (void)bpf_map_update_elem(&sock_map, &sk, sk_info, BPF_ANY);
}

#define __PERIOD ((u64)30 * 1000000000)
static __always_inline u64 get_period()
{
    u32 key = 0;
    u64 period = __PERIOD;
    struct tcp_args_s *args;

    args = (struct tcp_args_s *)bpf_map_lookup_elem(&args_map, &key);
    if (args)
        period = args->period;

    return period; // units from second to nanosecond
}

static __always_inline void report(void *ctx, struct tcp_metrics_s *metrics, u32 new_entry)
{
    if (new_entry) {
        (void)bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, metrics, sizeof(struct tcp_metrics_s));
    } else {
        u64 ts = bpf_ktime_get_ns();
        u64 period = get_period();
        if ((ts > metrics->ts) && ((ts - metrics->ts) < period)) {
            return;
        }
        metrics->ts = ts;
        (void)bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, metrics, sizeof(struct tcp_metrics_s));
    }
    __builtin_memset(&(metrics->data.health), 0x0, sizeof(metrics->data.health));
    __builtin_memset(&(metrics->data.info), 0x0, sizeof(metrics->data.info));
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

static void do_load_tcp_fd(u32 tgid, int fd, struct tcp_sock_info *info)
{
    int ret;
    struct sock *sk;
    struct tcp_link_s link = {0};
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    u32 syn_srtt_unuse;
    if (fd == 0)
        return;

    sk = sock_get_by_fd(fd, task);
    if (sk == (struct sock *)0)
        return;

    ret = create_sock_obj(tgid, sk, info);
    if (ret < 0)
        return;

    ret = get_tcp_link_key(&link, sk, &syn_srtt_unuse);
    if (ret < 0)
        return;

    bpf_printk("load tcp fd(cip=%x, sip=%x).\n", link.c_ip, link.s_ip);
}

static void load_tcp_fd(u32 tgid)
{
    struct tcp_fd_info *tcp_fd_s = bpf_map_lookup_elem(&tcp_fd_map, &tgid);
    struct tcp_sock_info tcp_sock_data = {0};
    if (!tcp_fd_s)
        return;

#pragma clang loop unroll(full)
    for (int i = 0; i < TCP_FD_PER_PROC_MAX; i++) {
        tcp_sock_data.role = tcp_fd_s->fd_role[i];
        tcp_sock_data.syn_srtt = 0;
        tcp_sock_data.tgid = tgid;
        do_load_tcp_fd(tgid, tcp_fd_s->fds[i], &tcp_sock_data);
    }

    (void)bpf_map_delete_elem(&tcp_fd_map, &tgid);
}

static void get_tcp_wnd(struct sock *sk, struct tcp_state* info)
{
    struct tcp_sock *tcp_sk = (struct tcp_sock *)sk;
    u32 write_seq = _(tcp_sk->write_seq);
    u32 snd_nxt = _(tcp_sk->snd_nxt);
    u32 snd_wnd = _(tcp_sk->snd_wnd);
    u32 snd_una = _(tcp_sk->snd_una);
    u32 rcv_wnd = _(tcp_sk->rcv_wnd);

    if (write_seq > snd_nxt) {
        info->tcpi_notsent_bytes = max(write_seq - snd_nxt, info->tcpi_notsent_bytes);
    }

    if (snd_nxt > snd_una) {
        info->tcpi_notack_bytes = max(snd_nxt - snd_una, info->tcpi_notack_bytes);
    }

    info->tcpi_snd_wnd = min_zero(info->tcpi_snd_wnd, snd_wnd);
    info->tcpi_rcv_wnd = min_zero(info->tcpi_rcv_wnd, rcv_wnd);
}

static void tcp_compute_busy_time(struct tcp_sock *tcp_sk, struct tcp_state* info)
{
    u32 i;
    u8 chrono_type;
    u32 chrono_stat[3] = {0};
    u32 chrono_start;
    u64 total = 0;
    u64 stats[__TCP_CHRONO_MAX];
    u64 ms = bpf_ktime_get_ns() >> 6; // ns -> ms

    chrono_start = _(tcp_sk->chrono_start);
    bpf_probe_read(chrono_stat, 3 * sizeof(u32), &(tcp_sk->chrono_stat));
    bpf_probe_read(&chrono_type, sizeof(u8), (char *)&(tcp_sk->chrono_stat) + 3 * sizeof(u32));

    chrono_type &= 0xC0;

#pragma clang loop unroll(full)
    for (i = TCP_CHRONO_BUSY; i < __TCP_CHRONO_MAX; ++i) {
        stats[i] = chrono_stat[i - 1];
        if (i == chrono_type)
            stats[i] += (ms > chrono_start) ? (ms - chrono_start) : 0;
        stats[i] *= USEC_PER_SEC / HZ;
        total += stats[i];
    }

    info->tcpi_busy_time = total;
    info->tcpi_rwnd_limited = stats[TCP_CHRONO_RWND_LIMITED];
    info->tcpi_sndbuf_limited = stats[TCP_CHRONO_SNDBUF_LIMITED];
}

static void tcp_compute_delivery_rate(struct tcp_sock *tcp_sk, struct tcp_state* info)
{
    u32 rate = _(tcp_sk->rate_delivered);
    u32 intv = _(tcp_sk->rate_interval_us);
    u32 mss_cache = _(tcp_sk->mss_cache);
    u64 rate64 = 0;

    if (rate && intv) {
        rate64 = (u64)rate * mss_cache * USEC_PER_SEC;
    }

    info->tcpi_delivery_rate = min_zero(info->tcpi_delivery_rate, rate64);
    return;
}

static __always_inline unsigned int jiffies_to_usecs(unsigned long j)
{
    return (USEC_PER_SEC / HZ) * j;
}

static void get_tcp_health(struct sock *sk, struct tcp_health* health)
{
    u32 tmp;
    struct tcp_sock *tcp_sk = (struct tcp_sock *)sk;

    tmp = _(sk->sk_drops.counter);
    health->sk_drops = max(health->sk_drops, tmp);

    tmp = _(tcp_sk->lost_out);
    health->lost_out = max(health->lost_out, tmp);

    tmp = _(tcp_sk->sacked_out);
    health->sacked_out = max(health->sacked_out, tmp);
}

static void get_tcp_info(struct sock *sk, struct tcp_state* info)
{
    u32 tmp;
    struct tcp_sock *tcp_sk = (struct tcp_sock *)sk;
    struct inet_connection_sock *icsk = (struct inet_connection_sock *)sk;

    tmp = jiffies_to_usecs(_(icsk->icsk_rto));
    info->tcpi_rto = max(info->tcpi_rto, tmp);

    tmp = jiffies_to_usecs(_(icsk->icsk_ack.ato));
    info->tcpi_ato = max(info->tcpi_ato, tmp);

    tmp = _(tcp_sk->srtt_us) >> 3;
    info->tcpi_srtt = max(info->tcpi_srtt, tmp);

    tmp = _(tcp_sk->snd_ssthresh);
    info->tcpi_snd_ssthresh = min_zero(info->tcpi_snd_ssthresh, tmp);

    tmp = _(tcp_sk->rcv_ssthresh);
    info->tcpi_rcv_ssthresh = min_zero(info->tcpi_rcv_ssthresh, tmp);

    tmp = _(tcp_sk->snd_cwnd);
    info->tcpi_snd_cwnd = min_zero(info->tcpi_snd_cwnd, tmp);

    tmp = _(tcp_sk->advmss);
    info->tcpi_advmss = max(info->tcpi_advmss, tmp);

    tmp = _(tcp_sk->reordering);
    info->tcpi_reordering = max(info->tcpi_reordering, tmp);

    tmp = _(tcp_sk->rcv_rtt_est.rtt_us);
    tmp = tmp >> 3;
    info->tcpi_rcv_rtt = max(info->tcpi_rcv_rtt, tmp);

    tmp = _(tcp_sk->rcvq_space.space);
    info->tcpi_rcv_space = min_zero(info->tcpi_rcv_space, tmp);

    tcp_compute_delivery_rate(tcp_sk, info);

    tcp_compute_busy_time(tcp_sk, info);

    tmp = _(sk->sk_pacing_rate);
    if (tmp != ~0U) {
        info->tcpi_pacing_rate = min_zero(info->tcpi_pacing_rate, tmp);
    }

    tmp = _(sk->sk_max_pacing_rate);
    if (tmp != ~0U) {
        info->tcpi_max_pacing_rate = min_zero(info->tcpi_max_pacing_rate, tmp);
    }

    tmp = _(sk->sk_error_queue.qlen);
    info->tcpi_sk_err_que_size = max(info->tcpi_sk_err_que_size, tmp);

    tmp = _(sk->sk_receive_queue.qlen);
    info->tcpi_sk_rcv_que_size = max(info->tcpi_sk_rcv_que_size, tmp);

    tmp = _(sk->sk_write_queue.qlen);
    info->tcpi_sk_wri_que_size = max(info->tcpi_sk_wri_que_size, tmp);

    tmp = (u32)_(sk->sk_backlog.len);
    info->tcpi_sk_backlog_size = max(info->tcpi_sk_backlog_size, tmp);

    tmp = (u32)_(sk->sk_omem_alloc.counter);
    info->tcpi_sk_omem_size = max(info->tcpi_sk_omem_size, tmp);

    tmp = (u32)_(sk->sk_forward_alloc);
    info->tcpi_sk_forward_size = max(info->tcpi_sk_forward_size, tmp);

    tmp = (u32)_(sk->sk_wmem_alloc.refs.counter);
    info->tcpi_sk_wmem_size = max(info->tcpi_sk_wmem_size, tmp);
}

KPROBE(tcp_set_state, pt_regs)
{
    struct tcp_sock_info tcp_sock_data = {0};
    u16 new_state = (u16)PT_REGS_PARM2(ctx);
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct tcp_sock *tcp_sock = (struct tcp_sock *)sk;
    u16 old_state = _(sk->sk_state);

    if (old_state == TCP_SYN_SENT && new_state == TCP_ESTABLISHED) {
        /* create sock object */
        tcp_sock_data.role = LINK_ROLE_CLIENT;
        (void)create_sock_obj(0, sk, &tcp_sock_data);
    }

    if (old_state == TCP_SYN_RECV && new_state == TCP_ESTABLISHED) {
        /* create sock object */
        tcp_sock_data.role = LINK_ROLE_SERVER;
        tcp_sock_data.syn_srtt = _(tcp_sock->srtt_us) >> 3;
        (void)create_sock_obj(0, sk, &tcp_sock_data);
    }

    if (new_state == TCP_CLOSE || new_state == TCP_CLOSE_WAIT || new_state == TCP_FIN_WAIT1) {
        (void)delete_tcp_link(sk);
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

    update_sock_obj(sk, tgid);

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_TX_XADD(metrics->data, size);
        get_tcp_info(sk, &(metrics->data.info));
        get_tcp_health(sk, &(metrics->data.health));
        get_tcp_wnd(sk, &(metrics->data.info));
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

    update_sock_obj(sk, tgid);

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        get_tcp_info(sk, &(metrics->data.info));
        get_tcp_health(sk, &(metrics->data.health));
        get_tcp_wnd(sk, &(metrics->data.info));
        report(ctx, metrics, new_entry);
    }
}

KPROBE_RET(tcp_add_backlog, pt_regs, CTX_KERNEL)
{
    u32 new_entry = 0;
    bool discard = (bool)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_add_backlog, ctx, val, CTX_KERNEL) < 0)
        return;

    if (discard) {
        sk = (struct sock *)PROBE_PARM1(val);

        metrics = get_tcp_metrics(sk, &new_entry);
        if (metrics) {
            TCP_BACKLOG_DROPS_INC(metrics->data);
            report(ctx, metrics, new_entry);
        }
    }
}

KPROBE_RET(tcp_filter, pt_regs, CTX_KERNEL)
{
    u32 new_entry = 0;
    bool discard = (bool)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_filter, ctx, val, CTX_KERNEL) < 0)
        return;

    if (discard) {

        sk = (struct sock *)PROBE_PARM1(val);
        metrics = get_tcp_metrics(sk, &new_entry);
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
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_TMOUT_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_cleanup_rbuf, pt_regs)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    int copied = (int)PT_REGS_PARM2(ctx);
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if (copied <= 0)
        return;

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_RX_XADD(metrics->data, copied);
        report(ctx, metrics, new_entry);
    }
}

KRAWTRACE(sock_exceed_buf_limit, bpf_raw_tracepoint_args)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock*)ctx->args[0];
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_SNDBUF_LIMIT_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KRAWTRACE(tcp_send_reset, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_SEND_RSTS_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KRAWTRACE(tcp_receive_reset, bpf_raw_tracepoint_args)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)ctx->args[0];
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_RECEIVE_RSTS_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_retransmit_skb, pt_regs)
{
    u32 new_entry __maybe_unused = 0;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    int segs = (int)PT_REGS_PARM3(ctx);
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_RETRANS_INC(metrics->data, segs);
        report(ctx, metrics, new_entry);
    }
}

KPROBE(tcp_done, pt_regs)
{
    u32 new_entry = 0;
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    unsigned char state = _(sk->sk_state);
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    if ((state == TCP_SYN_SENT || state == TCP_SYN_RECV)) {
        metrics = get_tcp_metrics(sk, &new_entry);
        if (metrics) {
            TCP_ATTEMPT_FAILED_INC(metrics->data);
            report(ctx, metrics, new_entry);
        }
    }
}

KPROBE_RET(tcp_try_rmem_schedule, pt_regs, CTX_KERNEL)
{
    u32 new_entry = 0;
    int ret = (int)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;
    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_try_rmem_schedule, ctx, val, CTX_KERNEL) < 0)
        return;

    if (ret == 0) {
        return;
    }

    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_RMEM_SCHEDULS_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }

    return;
}

KPROBE_RET(tcp_check_oom, pt_regs, CTX_KERNEL)
{
    u32 new_entry = 0;
    bool ret = (bool)PT_REGS_RC(ctx);
    struct sock *sk;
    struct probe_val val;

    struct tcp_metrics_s *metrics;

    if (PROBE_GET_PARMS(tcp_check_oom, ctx, val, CTX_KERNEL) < 0)
        return;

    if (!ret) {
        return;
    }

    sk = (struct sock *)PROBE_PARM1(val);
    if (sk == (void *)0) {
        return;
    }

    metrics = get_tcp_metrics(sk, &new_entry);
    if (metrics) {
        TCP_OOM_INC(metrics->data);
        report(ctx, metrics, new_entry);
    }

    return;
}
