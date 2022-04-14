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
 * Description: tcp_probe include file
 ******************************************************************************/
#ifndef __TCPPROBE__H
#define __TCPPROBE__H


#define LINK_ROLE_SERVER 0
#define LINK_ROLE_CLIENT 1
#define LINK_ROLE_MAX 2

#define TCP_FD_PER_PROC_MAX (10)

#define BPF_F_INDEX_MASK    0xffffffffULL
#define BPF_F_CURRENT_CPU   BPF_F_INDEX_MASK

struct tcp_fd_info {
    int fds[TCP_FD_PER_PROC_MAX];
    __u8 fd_role[TCP_FD_PER_PROC_MAX];
    unsigned int cnt;
};

struct tcp_status {
    __u32 srtt_last;        // FROM tcp_sock.srtt_us
    __u32 srtt_max;         // FROM tcp_sock.srtt_us
    __u32 srtt_min;         // FROM tcp_sock.srtt_us
    __u32 rcv_wnd_last;     // FROM tcp_sock.rcv_wnd
    __u32 rcv_wnd_max;      // FROM tcp_sock.rcv_wnd
    __u32 rcv_wnd_min;      // FROM tcp_sock.rcv_wnd
    __u32 snd_wnd_last;     // FROM tcp_sock.snd_wnd
    __u32 send_rsts;        // FROM tcp_send_reset event
    __u32 receive_rsts;     // FROM tcp_receive_reset event

    int snd_mem_last;       // FROM sock.sk_wmem_alloc
    int snd_mem_max;        // FROM sock.sk_wmem_alloc
    int snd_mem_min;        // FROM sock.sk_wmem_alloc
    int rcv_mem_last;       // FROM sock.sk_rmem_alloc
    int rcv_mem_max;        // FROM sock.sk_rmem_alloc
    int rcv_mem_min;        // FROM sock.sk_rmem_alloc
    int omem_alloc;         // FROM sock.sk_omem_alloc
    int forward_mem;        // FROM sock.sk_forward_alloc
    __u32 rcv_buf_limit;    // FROM sock.sk_rcvbuf
    __u32 snd_buf_limit;    // FROM sock.sk_sndbuf
    __u32 pacing_rate_last; // FROM sock.sk_pacing_rate
    __u32 pacing_rate_max;  // FROM sock.sk_pacing_rate
    __u32 pacing_rate_min;  // FROM sock.sk_pacing_rate

    __u32 ecn_flags;        // ECN status bits, 8bits, FROM tcp_sock.ecn_flags
    __u32 reord_seen;       // number of data packet reordering events, FROM tcp_sock.reord_seen
};

struct tcp_health {
    __u64 rx;               // FROM tcp_cleanup_rbuf
    __u64 tx;               // FROM tcp_sendmsg

    __u32 total_retrans;    // FROM tcp_retransmit_skb event
    __u32 synack_retrans;   // FROM tcp_retransmit_synack
    __u32 backlog_drops;    // FROM tcp_add_backlog event
    __u32 sk_drops;         // FROM tcp_drop
    __u32 md5_hash_drops;   // FROM tcp_v4_inbound_md5_hash event
    __u32 filter_drops;     // FROM tcp_filter event
    __u32 tmout;            // FROM tcp_write_err event
    __u32 rcvque_full;      // FROM sock_rcvqueue_full event
    __u32 sndbuf_limit;     // FROM sock_exceed_buf_limit event
    __u32 attempt_fails;    // FROM tcp_done event
    __u32 rmem_scheduls;    // FROM tcp_try_rmem_schedule event
    __u32 tcp_oom;          // FROM tcp_check_oom event

    int sk_err;             // FROM sock.sk_err
    int sk_err_soft;        // FROM sock.sk_err_soft
};

struct tcp_statistics {
    struct tcp_status status;
    struct tcp_health health;
};

#define TCP_STATE_UPDATE(data, sk) \
    do { \
        __u32 __tmp; \
        struct tcp_sock *__tcp_sock = (struct tcp_sock *)(sk); \
        (data).health.sk_err = _((sk)->sk_err); \
        (data).health.sk_err_soft = _((sk)->sk_err_soft); \
        __tmp = _(__tcp_sock->srtt_us) >> 3; \
        if ((data).status.srtt_last == 0) { \
            (data).status.srtt_max = __tmp; \
            (data).status.srtt_min = __tmp; \
        } else { \
            (data).status.srtt_min = (data).status.srtt_min > __tmp ? __tmp : (data).status.srtt_min; \
            (data).status.srtt_max = (data).status.srtt_max < __tmp ? __tmp : (data).status.srtt_max; \
        } \
        (data).status.srtt_last = __tmp; \
        \
        __tmp = _(__tcp_sock->rcv_wnd); \
        if ((data).status.rcv_wnd_last == 0) { \
            (data).status.rcv_wnd_max = __tmp; \
            (data).status.rcv_wnd_min = __tmp; \
        } else { \
            (data).status.rcv_wnd_min = (data).status.rcv_wnd_min > __tmp ? __tmp : (data).status.rcv_wnd_min; \
            (data).status.rcv_wnd_max = (data).status.rcv_wnd_max < __tmp ? __tmp : (data).status.rcv_wnd_max; \
        } \
        (data).status.rcv_wnd_last = __tmp; \
        \
        bpf_probe_read(&__tmp, sizeof(int), &((sk)->sk_backlog)); \
        if ((data).status.rcv_mem_last == 0) { \
            (data).status.rcv_mem_min = __tmp; \
            (data).status.rcv_mem_max = __tmp; \
        } else { \
            (data).status.rcv_mem_min = (data).status.rcv_mem_min > __tmp ? __tmp : (data).status.rcv_mem_min; \
            (data).status.rcv_mem_max = (data).status.rcv_mem_max < __tmp ? __tmp : (data).status.rcv_mem_max; \
        } \
        (data).status.rcv_mem_last = __tmp; \
        \
        bpf_probe_read(&((data).status.omem_alloc), sizeof(int), &((sk)->sk_omem_alloc)); \
        (data).status.forward_mem = _((sk)->sk_forward_alloc); \
        (data).status.rcv_buf_limit = _((sk)->sk_rcvbuf); \
        (data).status.ecn_flags = _(__tcp_sock->ecn_flags); \
    } while (0)

#define SND_TCP_STATE_UPDATE(data, sk) \
    do { \
        int __tmp; \
        struct tcp_sock *__tcp_sock = (struct tcp_sock *)(sk); \
        bpf_probe_read(&__tmp, sizeof(int), &((sk)->sk_wmem_alloc)); \
        if ((data).status.snd_mem_last == 0) { \
            (data).status.snd_mem_min = __tmp; \
            (data).status.snd_mem_max = __tmp; \
        } else { \
            (data).status.snd_mem_min = (data).status.snd_mem_min > __tmp ? __tmp : (data).status.snd_mem_min; \
            (data).status.snd_mem_max = (data).status.snd_mem_max < __tmp ? __tmp : (data).status.snd_mem_max; \
        } \
        (data).status.snd_mem_last = __tmp; \
        \
        __tmp = _((sk)->sk_pacing_rate); \
        if ((data).status.pacing_rate_last == 0) { \
            (data).status.pacing_rate_min = __tmp; \
            (data).status.pacing_rate_max = __tmp; \
        } else { \
            (data).status.pacing_rate_min = \
                (data).status.pacing_rate_min > __tmp ? __tmp : (data).status.pacing_rate_min; \
            (data).status.pacing_rate_max = \
                (data).status.pacing_rate_max < __tmp ? __tmp : (data).status.pacing_rate_max; \
        } \
        (data).status.pacing_rate_last = __tmp; \
        \
        (data).status.snd_buf_limit = _((sk)->sk_sndbuf); \
        (data).status.snd_wnd_last = _(__tcp_sock->snd_wnd); \
    } while (0)

#define TCP_BACKLOG_DROPS_INC(data) __sync_fetch_and_add(&((data).health.backlog_drops), 1)
#define TCP_SK_DROPS_INC(data) __sync_fetch_and_add(&((data).health.sk_drops), 1)
#define TCP_MD5_DROPS_INC(data) __sync_fetch_and_add(&((data).health.md5_hash_drops), 1)
#define TCP_FILTER_DROPS_INC(data) __sync_fetch_and_add(&((data).health.filter_drops), 1)
#define TCP_TMOUT_INC(data) __sync_fetch_and_add(&((data).health.tmout), 1)
#define TCP_SNDBUF_LIMIT_INC(data) __sync_fetch_and_add(&((data).health.sndbuf_limit), 1)
#define TCP_RCVQUE_FULL_INC(data) __sync_fetch_and_add(&((data).health.rcvque_full), 1)
#define TCP_SEND_RSTS_INC(data) __sync_fetch_and_add(&((data).status.send_rsts), 1)
#define TCP_RECEIVE_RSTS_INC(data) __sync_fetch_and_add(&((data).status.receive_rsts), 1)
#define TCP_RETRANS_INC(data) __sync_fetch_and_add(&((data).health.total_retrans), 1)

#define TCP_ATTEMPT_FAILED_INC(data) __sync_fetch_and_add(&((data).health.attempt_fails), 1)
#define TCP_RMEM_SCHEDULS_INC(data) __sync_fetch_and_add(&((data).health.rmem_scheduls), 1)
#define TCP_OOM_INC(data) __sync_fetch_and_add(&((data).health.tcp_oom), 1)

#define TCP_RX_XADD(data, delta) __sync_fetch_and_add(&((data).health.rx), (__u64)(delta))
#define TCP_TX_XADD(data, delta) __sync_fetch_and_add(&((data).health.tx), (__u64)(delta))

struct tcp_link_s {
    union {
        __u32 c_ip;
        unsigned char c_ip6[IP6_LEN];
    };
    union {
        __u32 s_ip;
        unsigned char s_ip6[IP6_LEN];
    };
    __u16 s_port;
    __u16 family;
    __u32 tgid;     // process id
    __u32 role;     // role: client:1/server:0
};

struct tcp_metrics_s {
    __u64 ts;
    struct tcp_link_s link;
    struct tcp_statistics data;
};

#endif
