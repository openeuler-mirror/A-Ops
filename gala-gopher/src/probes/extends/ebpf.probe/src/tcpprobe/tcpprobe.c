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
 * Description: tcp_probe user prog
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "tcp.h"
#include "args.h"
#include "tcpprobe.skel.h"
#include "tcpprobe.h"

#define OO_NAME "tcp_link"  // Observation Object name
#define OO_TYPE_STATUS "status"
#define OO_TYPE_HEALTH "health"
#define TCP_LINK_TMOUT  (5 * 60)    // 5 min

static struct probe_params params = {.period = DEFAULT_PERIOD,
                                     .cport_flag = 0};

static void print_link_metrics(void *ctx, int cpu, void *data, __u32 size)
{
    struct tcp_link_s *link;
    struct tcp_metrics_s *metrics  = (struct tcp_metrics_s *)data;

    link = &(metrics->link);
    
    unsigned char src_ip_str[INET6_ADDRSTRLEN];
    unsigned char dst_ip_str[INET6_ADDRSTRLEN];

    ip_str(link->family, (unsigned char *)&(link->c_ip), src_ip_str, INET6_ADDRSTRLEN);
    ip_str(link->family, (unsigned char *)&(link->s_ip), dst_ip_str, INET6_ADDRSTRLEN);
    // status infos
    fprintf(stdout,
        "|%s_%s|%u|%u|%s|%s|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%d|%d|%d|%u|%u|%u|%d|%d|%d|%u|%u|%u|%d|%d|%u|%u|%u|%u|%u|%u|\n",
        OO_NAME,
        OO_TYPE_STATUS,
        link->tgid,
        link->role,
        src_ip_str,
        dst_ip_str,
        link->c_port,
        link->s_port,
        link->family,
        metrics->data.status.srtt_last,
        metrics->data.status.srtt_max,
        metrics->data.status.srtt_min,
        metrics->data.syn_status.syn_srtt_last,
        metrics->data.syn_status.syn_srtt_max,
        metrics->data.syn_status.syn_srtt_min,
        metrics->data.status.rcv_wnd_last,
        metrics->data.status.rcv_wnd_max,
        metrics->data.status.rcv_wnd_min,
        metrics->data.status.snd_wnd_last,
        metrics->data.status.send_rsts,
        metrics->data.status.receive_rsts,
        metrics->data.status.snd_mem_last,
        metrics->data.status.snd_mem_max,
        metrics->data.status.snd_mem_min,
        metrics->data.status.snd_que_last,
        metrics->data.status.snd_que_max,
        metrics->data.status.snd_que_min,
        metrics->data.status.rcv_mem_last,
        metrics->data.status.rcv_mem_max,
        metrics->data.status.rcv_mem_min,
        metrics->data.status.rcv_que_last,
        metrics->data.status.rcv_que_max,
        metrics->data.status.rcv_que_min,
        metrics->data.status.omem_alloc,
        metrics->data.status.forward_mem,
        metrics->data.status.rcv_buf_limit,
        metrics->data.status.snd_buf_limit,
        metrics->data.status.pacing_rate_last,
        metrics->data.status.pacing_rate_max,
        metrics->data.status.pacing_rate_min,
        metrics->data.status.ecn_flags);
    // health infos
    fprintf(stdout,
        "|%s_%s|%u|%u|%s|%s|%u|%u|%u|%llu|%llu|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%d|%d|\n",
        OO_NAME,
        OO_TYPE_HEALTH,
        link->tgid,
        link->role,
        src_ip_str,
        dst_ip_str,
        link->c_port,
        link->s_port,
        link->family,
        metrics->data.health.rx,
        metrics->data.health.tx,
        metrics->data.health.total_retrans,
        metrics->data.health.sk_drops,
        metrics->data.health.backlog_drops,
        metrics->data.health.filter_drops,
        metrics->data.health.tmout,
        metrics->data.health.rcvque_full,
        metrics->data.health.sndbuf_limit,
        metrics->data.health.attempt_fails,
        metrics->data.health.rmem_scheduls,
        metrics->data.health.tcp_oom,
        metrics->data.health.sk_err,
        metrics->data.health.sk_err_soft);
    (void)fflush(stdout);
}

static void load_period(int period_fd, __u32 value)
{
    __u32 key = 0;
    __u64 period = (__u64)value * 1000000000;
    (void)bpf_map_update_elem(period_fd, &key, &period, BPF_ANY);
}

static void load_cport_flag(int cport_flag_fd, __u32 value)
{
    __u32 key = 0;
    (void)bpf_map_update_elem(cport_flag_fd, &key, &value, BPF_ANY);
}

static void do_load_tcp_fd(int tcp_fd_map_fd, __u32 tgid, int fd, __u8 role)
{
    struct tcp_fd_info tcp_fd_s = {0};
    char *role_name[LINK_ROLE_MAX] = {"client", "server"};

    (void)bpf_map_lookup_elem(tcp_fd_map_fd, &tgid, &tcp_fd_s);
    if (tcp_fd_s.cnt >= TCP_FD_PER_PROC_MAX)
        return;

    tcp_fd_s.fds[tcp_fd_s.cnt] = fd;
    tcp_fd_s.fd_role[tcp_fd_s.cnt] = role;
    tcp_fd_s.cnt++;
    (void)bpf_map_update_elem(tcp_fd_map_fd, &tgid, &tcp_fd_s, BPF_ANY);
    INFO("Update establish(tgid = %u, fd = %d, role = %s).\n", tgid, fd, role_name[role]);
}

static void load_tcp_fd(int tcp_fd_map_fd)
{
    int i, j;
    __u8 role;
    struct tcp_listen_ports* tlps;
    struct tcp_estabs* tes = NULL;

    tlps = get_listen_ports();
    if (tlps == NULL)
        goto err;

    tes = get_estab_tcps(tlps);
    if (tes == NULL)
        goto err;

    /* insert tcp establish into map */
    for (i = 0; i < tes->te_num; i++) {
        role = tes->te[i]->is_client == 1 ? LINK_ROLE_CLIENT : LINK_ROLE_SERVER;
        for (j = 0; j < tes->te[i]->te_comm_num; j++) {
            do_load_tcp_fd(tcp_fd_map_fd,
                (__u32)tes->te[i]->te_comm[j]->pid, (int)tes->te[i]->te_comm[j]->fd, role);
        }
    }

err:
    if (tlps)
        free_listen_ports(&tlps);

    if (tes)
        free_estab_tcps(&tes);

    return;
}

int main(int argc, char **argv)
{
    int err = -1;
    int out_put_fd = -1;
    struct perf_buffer* pb = NULL;

    err = args_parse(argc, argv, "t:c:", &params);
    if (err != 0)
        return -1;

    printf("arg parse interval time:%us\n", params.period);
    printf("arg parse cport flag:%u\n", params.cport_flag);

    INIT_BPF_APP(tcpprobe, EBPF_RLIM_LIMITED);
    LOAD(tcpprobe, err);

    out_put_fd = GET_MAP_FD(tcpprobe, output);
    pb = create_pref_buffer(out_put_fd, print_link_metrics);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    load_tcp_fd(GET_MAP_FD(tcpprobe, tcp_fd_map));
    load_period(GET_MAP_FD(tcpprobe, period_map), params.period);
    load_cport_flag(GET_MAP_FD(tcpprobe, cport_flag_map), params.cport_flag);

    printf("Successfully started!\n");

    poll_pb(pb, THOUSAND);

err:
    if (pb)
        perf_buffer__free(pb);

    UNLOAD(tcpprobe);
    return -err;
}
