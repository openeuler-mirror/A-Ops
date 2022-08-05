/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: luzhihao
 * Create: 2022-07-28
 * Description: tcp sockbuf probe
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include <bpf/bpf_endian.h>
#include "bpf.h"
#include "tcp_link.h"

char g_linsence[] SEC("license") = "GPL";

static __always_inline char is_tmout_sockbuf(struct sock *sk)
{
    struct sock_stats_s *sock_stats = bpf_map_lookup_elem(&tcp_link_map, &sk);
    if (!sock_stats) {
        return 0;
    }

    u64 ts = bpf_ktime_get_ns();
    u64 period = get_period();
    if ((ts > sock_stats->ts_stats.sockbuf_ts) && ((ts - sock_stats->ts_stats.sockbuf_ts) >= period)) {
        sock_stats->ts_stats.sockbuf_ts = ts;
        return 1;
    }
    return 0;
}

static __always_inline void report_sockbuf(void *ctx, struct tcp_metrics_s *metrics)
{
    metrics->report_flags |= TCP_PROBE_SOCKBUF;

    (void)bpf_perf_event_output(ctx, &tcp_output, BPF_F_CURRENT_CPU, metrics, sizeof(struct tcp_metrics_s));

    metrics->report_flags &= ~TCP_PROBE_SOCKBUF;
    __builtin_memset(&(metrics->sockbuf_stats), 0x0, sizeof(metrics->sockbuf_stats));
}

static void get_tcp_sock_buf(struct sock *sk, struct tcp_sockbuf* stats)
{
    u32 tmp;

    tmp = _(sk->sk_error_queue.qlen);
    stats->tcpi_sk_err_que_size = max(stats->tcpi_sk_err_que_size, tmp);

    tmp = _(sk->sk_receive_queue.qlen);
    stats->tcpi_sk_rcv_que_size = max(stats->tcpi_sk_rcv_que_size, tmp);

    tmp = _(sk->sk_write_queue.qlen);
    stats->tcpi_sk_wri_que_size = max(stats->tcpi_sk_wri_que_size, tmp);

    tmp = (u32)_(sk->sk_backlog.len);
    stats->tcpi_sk_backlog_size = max(stats->tcpi_sk_backlog_size, tmp);

    tmp = (u32)_(sk->sk_omem_alloc.counter);
    stats->tcpi_sk_omem_size = max(stats->tcpi_sk_omem_size, tmp);

    tmp = (u32)_(sk->sk_forward_alloc);
    stats->tcpi_sk_forward_size = max(stats->tcpi_sk_forward_size, tmp);

    tmp = (u32)_(sk->sk_wmem_alloc.refs.counter);
    stats->tcpi_sk_wmem_size = max(stats->tcpi_sk_wmem_size, tmp);
}

KRAWTRACE(tcp_probe, bpf_raw_tracepoint_args)
{
    struct sock *sk = (struct sock*)ctx->args[0];
    struct tcp_metrics_s *metrics;
    u32 pid __maybe_unused = bpf_get_current_pid_tgid();

    // Avoid high performance costs
    if (!is_tmout_sockbuf(sk)) {
        return;
    }

    metrics = get_tcp_metrics(sk);
    if (metrics) {
        get_tcp_sock_buf(sk, &(metrics->sockbuf_stats));
        report_sockbuf(ctx, metrics);
    }
}

