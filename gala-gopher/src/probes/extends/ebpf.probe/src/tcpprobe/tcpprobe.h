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

struct tcp_sock_info {
    __u32 role;     // client:1/server:0
    __u32 syn_srtt; // rtt from SYN/ACK to ACK
    __u32 tgid;     // PID
};

struct tcp_syn_status {
    __u32 syn_srtt_last;    // FROM tcp_sock.srtt_us when old_state = RCV_SYNC & new_state = EATAB
    //__u32 syn_srtt_max;     // FROM tcp_sock.srtt_us when old_state = RCV_SYNC & new_state = EATAB
    //__u32 syn_srtt_min;     // FROM tcp_sock.srtt_us when old_state = RCV_SYNC & new_state = EATAB
};

struct tcp_health {
    __u32 total_retrans;    // FROM tcp_retransmit_skb event
    __u32 backlog_drops;    // FROM tcp_add_backlog event
    __u32 sk_drops;         // FROM tcp_drop
    __u32 filter_drops;     // FROM tcp_filter event
    __u32 tmout;            // FROM tcp_write_err event
    __u32 sndbuf_limit;     // FROM sock_exceed_buf_limit event
    __u32 attempt_fails;    // FROM tcp_done event
    __u32 rmem_scheduls;    // FROM tcp_try_rmem_schedule event
    __u32 tcp_oom;          // FROM tcp_check_oom event
    __u32 send_rsts;        // FROM tcp_send_reset event
    __u32 receive_rsts;     // FROM tcp_receive_reset event

    int sk_err;             // FROM sock.sk_err
    int sk_err_soft;        // FROM sock.sk_err_soft
};

struct tcp_state {
    __u64 rx;                   // FROM tcp_cleanup_rbuf
    __u64 tx;                   // FROM tcp_sendmsg

    __u32   tcpi_rto;           // Retransmission timeOut(us)
    __u32   tcpi_ato;           // Estimated value of delayed ACK(us)

    /* Metrics. */
    __u32   tcpi_srtt;          // FROM tcp_sock.srtt_us in tcp_recvmsg
    __u32   tcpi_snd_ssthresh;  // Slow start threshold for congestion control.
    __u32   tcpi_rcv_ssthresh;  // Current receive window size.
    __u32   tcpi_snd_cwnd;      // Congestion Control Window Size.
    __u32   tcpi_advmss;        // Local MSS upper limit.
    __u32   tcpi_reordering;    // Segments to be reordered.

    __u32   tcpi_rcv_rtt;       // Receive end RTT (unidirectional measurement).
    __u32   tcpi_rcv_space;     // Current receive buffer size.

    __u32   tcpi_notsent_bytes; // Number of bytes not sent currently.
    __u32   tcpi_notack_bytes;  // Number of bytes not ack currently.
    __u32   tcpi_snd_wnd;       // FROM tcp_sock.snd_wnd
    __u32   tcpi_rcv_wnd;       // FROM tcp_sock.rcv_wnd

    __u64   tcpi_delivery_rate; // Current transmit rate (multiple different from the actual value).

    __u32   tcpi_busy_time;      // Time (jiffies) busy sending data.
    __u32   tcpi_rwnd_limited;   // Time (jiffies) limited by receive window.
    __u32   tcpi_sndbuf_limited; // Time (jiffies) limited by send buffer.

    __u32   tcpi_pacing_rate;    // bytes per second
    __u32   tcpi_max_pacing_rate;   // bytes per second

    __u32   tcpi_sk_err_que_size;   // FROM sock.sk_error_queue.qlen
    __u32   tcpi_sk_rcv_que_size;   // FROM sock.sk_receive_queue.qlen
    __u32   tcpi_sk_wri_que_size;   // FROM sock.sk_write_queue.qlen
    __u32   tcpi_sk_backlog_size;   // FROM sock.sk_backlog.len

    __u32   tcpi_sk_omem_size;      // FROM sock.sk_omem_alloc
    __u32   tcpi_sk_forward_size;   // FROM sock.sk_forward_alloc
    __u32   tcpi_sk_wmem_size;      // FROM sock.sk_wmem_alloc
};

struct tcp_statistics {
    struct tcp_syn_status syn_status;
    struct tcp_health health;
    struct tcp_state info;
};

#define TCP_BACKLOG_DROPS_INC(data) __sync_fetch_and_add(&((data).health.backlog_drops), 1)
#define TCP_SK_DROPS_INC(data) __sync_fetch_and_add(&((data).health.sk_drops), 1)
#define TCP_FILTER_DROPS_INC(data) __sync_fetch_and_add(&((data).health.filter_drops), 1)
#define TCP_TMOUT_INC(data) __sync_fetch_and_add(&((data).health.tmout), 1)
#define TCP_SNDBUF_LIMIT_INC(data) __sync_fetch_and_add(&((data).health.sndbuf_limit), 1)
#define TCP_SEND_RSTS_INC(data) __sync_fetch_and_add(&((data).health.send_rsts), 1)
#define TCP_RECEIVE_RSTS_INC(data) __sync_fetch_and_add(&((data).health.receive_rsts), 1)
#define TCP_RETRANS_INC(data, delta) __sync_fetch_and_add(&((data).health.total_retrans), (int)(delta))

#define TCP_ATTEMPT_FAILED_INC(data) __sync_fetch_and_add(&((data).health.attempt_fails), 1)
#define TCP_RMEM_SCHEDULS_INC(data) __sync_fetch_and_add(&((data).health.rmem_scheduls), 1)
#define TCP_OOM_INC(data) __sync_fetch_and_add(&((data).health.tcp_oom), 1)

#define TCP_RX_XADD(data, delta) __sync_fetch_and_add(&((data).info.rx), (__u64)(delta))
#define TCP_TX_XADD(data, delta) __sync_fetch_and_add(&((data).info.tx), (__u64)(delta))

struct tcp_link_s {
    __u32 tgid;     // process id
    union {
        __u32 c_ip;
        unsigned char c_ip6[IP6_LEN];
    };
    union {
        __u32 s_ip;
        unsigned char s_ip6[IP6_LEN];
    };
    __u16 s_port;   // server port
    __u16 c_port;   // client port
    __u16 family;
    __u16 c_flag;   // c_port valid:1/invalid:0
    __u32 role;     // role: client:1/server:0
};

struct tcp_metrics_s {
    __u64 ts;
    struct tcp_link_s link;
    struct tcp_statistics data;
};

#endif
