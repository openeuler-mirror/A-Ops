// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
/* Copyright (c) 2020 Facebook */
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
#include "nginx_probe.skel.h"
#include "nginx_probe.h"
#include "args.h"


static struct probe_params params = {.period = 5};
static volatile bool exiting = false;
static void sig_handler(int sig)
{
    exiting = true;
}

void update_statistic_map(int map_fd, struct ngx_metric *data)
{
    struct ngx_statistic_key k = {0};
    struct ngx_statistic v = {0};

    /* build key */
    memcpy(&k.cip, &(data->src_ip.ipaddr), sizeof(struct ip));
    k.family = data->src_ip.family;
    k.is_l7 = data->is_l7;
    memcpy(k.sip_str, data->dst_ip_str, INET6_ADDRSTRLEN);

    bpf_map_lookup_elem(map_fd, &k, &v);
    if (v.link_count == 0) {
        memcpy(&(v.ngx_ip), &(data->ngx_ip), sizeof(struct ip_addr));
    }
    v.link_count++;

    bpf_map_update_elem(map_fd, &k, &v, BPF_ANY);
    return;
}

void pull_probe_data(int map_fd, int statistic_map_fd)
{
    int ret = -1;
    struct ip_addr key = {0};
    struct ip_addr next_key = {0};
    struct ngx_metric data;
    unsigned char c_ip_str[INET6_ADDRSTRLEN];
    unsigned char c_local_ip_str[INET6_ADDRSTRLEN];

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &data);
        if (ret == 0) {
            ip_str(data.src_ip.family, (unsigned char *)&data.src_ip, c_ip_str, INET6_ADDRSTRLEN);
            ip_str(data.ngx_ip.family, (unsigned char *)&data.ngx_ip, c_local_ip_str, INET6_ADDRSTRLEN);

            printf("===ngx[%s]: %s:%d --> %s:%d --> %s\n",
                (data.is_l7 == 1 ? "7 LB" : "4 LB"),
                c_ip_str,
                ntohs(data.src_ip.port),
                c_local_ip_str,
                ntohs(data.ngx_ip.port),
                data.dst_ip_str);

            update_statistic_map(statistic_map_fd, &data);
        }

        if (data.is_finish) {
            bpf_map_delete_elem(map_fd, &next_key);
        } else {
            key = next_key;
        }
    }

    return;
}


#define METRIC_STATISTIC_NAME "nginx_link"
void print_statistic_map(int fd)
{
    int ret = 0;
    struct ngx_statistic_key k = {0};
    struct ngx_statistic_key nk = {0};
    struct ngx_statistic d = {0};

    unsigned char cip_str[INET6_ADDRSTRLEN];
    unsigned char ngxip_str[INET6_ADDRSTRLEN];
    unsigned char sip_str[INET6_ADDRSTRLEN];
    
    char *colon = NULL;

    while (bpf_map_get_next_key(fd, &k, &nk) != -1) {
        ret = bpf_map_lookup_elem(fd, &nk, &d);
        if (ret == 0) {
            ip_str(nk.family, (unsigned char *)&(nk.cip), cip_str, INET6_ADDRSTRLEN);
            ip_str(d.ngx_ip.family, (unsigned char *)&(d.ngx_ip.ipaddr), ngxip_str, INET6_ADDRSTRLEN);

            colon = strrchr(nk.sip_str, ':');
            if (colon) {
                *colon = '\0';
            }

            fprintf(stdout,
                "|%s|%s|%s|%s|%u|%s|%u|%u|\n",
                METRIC_STATISTIC_NAME,
                cip_str,
                ngxip_str,
                nk.sip_str,
		ntohs(d.ngx_ip.port),
                (colon ? (colon + 1) : "0"),
                nk.is_l7,
                d.link_count);

            if (colon) {
                *colon = ':';
            }
        }

        bpf_map_delete_elem(fd, &nk);
    }
    fflush(stdout);
    return;
}

int main(int argc, char **argv)
{
    int err;
    int map_fd = -1;

    err = args_parse(argc, argv, "t:", &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);

	LOAD(nginx_probe);

    /* Clean handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);


    int ret = 0;
    int ret2 = 0;
    UBPF_ATTACH(nginx_probe, nginx, ngx_stream_proxy_init_upstream,ret);
    UBPF_RET_ATTACH(nginx_probe, nginx, ngx_stream_proxy_init_upstream,ret);
    UBPF_ATTACH(nginx_probe, nginx, ngx_http_upstream_handler,ret2);
    ret |= ret2;
    if (ret == 0) {
        goto err;
    }
    UBPF_ATTACH(nginx_probe, nginx, ngx_close_connection,ret);
    if (ret == 0) {
        goto err;
    }

    /* create ngx statistic map_fd */
    map_fd = bpf_create_map(
        BPF_MAP_TYPE_HASH, sizeof(struct ngx_statistic_key), sizeof(struct ngx_statistic), STATISTIC_MAX_ENTRIES, 0);
    if (map_fd < 0) {
        printf("Failed to create statistic map fd.\n");
        goto err;
    }

    printf("Successfully started!\n");

    /* try to hit probe info */
    while (!exiting) {
        pull_probe_data(GET_MAP_FD(hs), map_fd);
        print_statistic_map(map_fd);
        sleep(params.period);
    }

err:
    if (map_fd > 0) {
        close(map_fd);
    }
    UNLOAD(nginx_probe);
    return 0;
}
