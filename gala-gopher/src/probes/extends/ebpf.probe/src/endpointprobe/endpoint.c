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
 * Description: endpoint_probe user prog
 ******************************************************************************/
#include <stdio.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include <bpf/bpf.h>
#include "bpf.h"
#include "args.h"
#include "endpoint.skel.h"
#include "endpoint.h"
#include "tcp.h"

#define OO_NAME "endpoint"

static volatile sig_atomic_t stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};

static void sig_int(int signo)
{
    stop = 1;
}

static int _init_ipaddr(struct ip *ip, const struct ip_addr *ip_addr)
{
    struct in_addr iaddr;
    struct in6_addr iaddr6;
    int ret;

    if (ip_addr->ipv4) {
        ret = inet_aton(ip_addr->ip, &iaddr);
        if (ret == 0) {
            return -1;
        }
        ip->ip.ip4 = (unsigned int)iaddr.s_addr;
        ip->family = AF_INET;
    } else {
        ret = inet_pton(AF_INET6, ip_addr->ip, &iaddr6);
        if (ret < 1) {
            return -1;
        }
        memcpy(ip->ip.ip6, &iaddr6, sizeof(ip->ip.ip6));
        ip->family = AF_INET6;
    }

    return 0;
}

static void _update_tcp_endpoint_to_map(int c_endpoint_map_fd, int listen_port_map_fd, int listen_sockfd_map_fd)
{
    int err;
    struct tcp_listen_ports *tlps = NULL;
    struct tcp_listen_port *tlp = NULL;
    struct listen_port_key_t listen_port_key = {0};
    struct listen_sockfd_key_t listen_sockfd_key = {0};
    unsigned short listen_port;

    struct tcp_estabs *tes = NULL;
    struct tcp_estab *te = NULL;
    struct tcp_estab_comm *tec = NULL;

    struct c_endpoint_key_t c_ep_key;
    struct endpoint_val_t ep_val;

    tlps = get_listen_ports();
    if (tlps == NULL) {
        goto err;
    }

    for (int i = 0; i < tlps->tlp_num; i++) {
        tlp = tlps->tlp[i];
        listen_port = (unsigned short)tlp->port;
        listen_port_key.tgid = tlp->pid;
        listen_port_key.protocol = IPPROTO_TCP;
        listen_port_key.port = listen_port;
        bpf_map_update_elem(listen_port_map_fd, &listen_port_key, &listen_port, BPF_ANY);
        listen_sockfd_key.tgid = tlp->pid;
        listen_sockfd_key.fd = tlp->fd;
        bpf_map_update_elem(listen_sockfd_map_fd, &listen_sockfd_key, &(tlp->fd), BPF_ANY);
    }

    tes = get_estab_tcps(tlps);
    if (tes == NULL) {
        goto err;
    }

    /* insert tcp client info into map */
    for (int i = 0; i < tes->te_num; i++) {
        te = tes->te[i];
        if (te->is_client != 1) {
            continue;
        }
        for (int j = 0; j < te->te_comm_num; j++) {
            tec = te->te_comm[j];
            memset(&c_ep_key, 0, sizeof(c_ep_key));
            memset(&ep_val, 0, sizeof(ep_val));

            // init endpoint key
            c_ep_key.tgid = tec->pid;
            err = _init_ipaddr(&c_ep_key.ip_addr, &te->local);
            if (err < 0) {
                break;
            }
            c_ep_key.protocol = IPPROTO_TCP;

            // init endpoint value
            ep_val.type = SK_TYPE_CLIENT_TCP;
            ep_val.tgid = c_ep_key.tgid;
            snprintf(ep_val.comm, sizeof(ep_val.comm), "%s", tec->comm);
            ep_val.s_type = SOCK_STREAM;
            ep_val.protocol = c_ep_key.protocol;
            memcpy(&ep_val.s_addr, &c_ep_key.ip_addr, sizeof(struct ip));

            bpf_map_update_elem(c_endpoint_map_fd, &c_ep_key, &ep_val, BPF_ANY);
        }
    }

err:
    if (tlps != NULL) {
        free_listen_ports(&tlps);
    }

    if (tes != NULL) {
        free_estab_tcps(&tes);
    }
}

static void _output_endpoint_data(struct endpoint_val_t *data)
{
    unsigned char s_addr[INET6_ADDRSTRLEN];

    ip_str(data->s_addr.family, (unsigned char *)&data->s_addr.ip, s_addr, INET6_ADDRSTRLEN);
    fprintf(stdout,
            "|%s|%d|%s|%d|%u|%d|%d|%d|%s|%u|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|\n",
            OO_NAME,
            data->tgid,
            data->comm,
            data->type,
            data->uid,
            data->s_addr.family,
            data->s_type,
            data->protocol,
            s_addr,
            data->s_port,
            data->ep_stats.stats[EP_STATS_LISTEN_DROPS],
            data->ep_stats.stats[EP_STATS_LISTEN_OVERFLOW],
            data->ep_stats.stats[EP_STATS_PASSIVE_OPENS],
            data->ep_stats.stats[EP_STATS_ACTIVE_OPENS],
            data->ep_stats.stats[EP_STATS_ATTEMPT_FAILS],
            data->ep_stats.stats[EP_STATS_ABORT_CLOSE],
            data->ep_stats.stats[EP_STATS_REQUEST_FAILS],
            data->ep_stats.stats[EP_STATS_RMEM_SCHEDULE],
            data->ep_stats.stats[EP_STATS_TCP_OOM],
            data->ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);

    return;
}

static void _print_endpoint_data(struct endpoint_val_t *data)
{
    unsigned char s_addr[INET6_ADDRSTRLEN];

    ip_str(data->s_addr.family, (unsigned char *)&data->s_addr.ip, s_addr, INET6_ADDRSTRLEN);
    DEBUG("[%d-%s] ep_type:%d, ep_uid:%u, ep_family:%d, ep_s_type:%d, ep_protocol:%d, "
            "ep_addr:%s, ep_port:%u, ep_listen_drops:%lu, ep_listen_overflows:%lu, "
            "ep_passive_opens:%lu, ep_active_opens:%lu, ep_attempt_fails:%lu, ep_abort_close:%lu, "
            "ep_request_fails:%lu, ep_rmem_schedule:%lu, ep_tcp_oom:%lu, ep_keepalive_timeout:%lu\n",
            data->tgid,
            data->comm,
            data->type,
            data->uid,
            data->s_addr.family,
            data->s_type,
            data->protocol,
            s_addr,
            data->s_port,
            data->ep_stats.stats[EP_STATS_LISTEN_DROPS],
            data->ep_stats.stats[EP_STATS_LISTEN_OVERFLOW],
            data->ep_stats.stats[EP_STATS_PASSIVE_OPENS],
            data->ep_stats.stats[EP_STATS_ACTIVE_OPENS],
            data->ep_stats.stats[EP_STATS_ATTEMPT_FAILS],
            data->ep_stats.stats[EP_STATS_ABORT_CLOSE],
            data->ep_stats.stats[EP_STATS_REQUEST_FAILS],
            data->ep_stats.stats[EP_STATS_RMEM_SCHEDULE],
            data->ep_stats.stats[EP_STATS_TCP_OOM],
            data->ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);

    return;
}

static void pull_endpoint_data(int s_ep_map_fd)
{
    int ret = 0;
    struct s_endpoint_key_t key = {0};
    struct s_endpoint_key_t next_key = {0};
    struct endpoint_val_t data = {0};

    while (bpf_map_get_next_key(s_ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(s_ep_map_fd, &next_key, &data);
        if (ret == 0) {
            _output_endpoint_data(&data);
            _print_endpoint_data(&data);
        }
        key = next_key;
    }

    return;
}

static void pull_client_endpoint_data(int c_ep_map_fd)
{
    int ret = 0;
    struct c_endpoint_key_t key = {0};
    struct c_endpoint_key_t next_key = {0};
    struct endpoint_val_t data = {0};

    while (bpf_map_get_next_key(c_ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(c_ep_map_fd, &next_key, &data);
        if (ret == 0) {
            _output_endpoint_data(&data);
            _print_endpoint_data(&data);
        }
        key = next_key;
    }

    return;
}


int main(int argc, char **argv)
{
    int err = -1;
    err = args_parse(argc, argv, "t:", &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);

	INIT_BPF_APP(endpoint, EBPF_RLIM_INFINITY);
    LOAD(endpoint, err);

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "Can't set signal handler: %d\n", errno);
        goto err;
    }

    _update_tcp_endpoint_to_map(GET_MAP_FD(endpoint, c_endpoint_map),
                                GET_MAP_FD(endpoint, listen_port_map),
                                GET_MAP_FD(endpoint, listen_sockfd_map));
    printf("Successfully started!\n");
    while (!stop) {
        pull_endpoint_data(GET_MAP_FD(endpoint, s_endpoint_map));
        pull_client_endpoint_data(GET_MAP_FD(endpoint, c_endpoint_map));

        sleep(params.period);
    }

err:
    UNLOAD(endpoint);
    return -err;
}
