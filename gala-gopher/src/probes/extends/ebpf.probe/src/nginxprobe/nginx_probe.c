// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
/* Copyright (c) 2020 Facebook */
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "nginx_probe.skel.h"
#include "nginx_probe.h"
#include "util.h"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    return vfprintf(stderr, format, args);
}

static void bump_memlock_rlimit(void)
{
    struct rlimit rlim_new = {
        .rlim_cur = RLIM_INFINITY,
        .rlim_max = RLIM_INFINITY,
    };

    if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
        fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
        exit(1);
    }
}

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
    int ret;
    struct sockaddr key = {0};
    struct sockaddr next_key = {0};
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

unsigned int g_print_interval_sec = 5;

void ngxprobe_arg_parse(char opt, char *arg, int idx)
{
    if (opt != 't' || !arg) {
        return;
    }

    unsigned int interval = (unsigned int)atoi(arg);
    if (interval < MIN_PRINT_INTERVAL || interval > MAX_PRINT_INTERVAL) {
        return;
    }
    g_print_interval_sec = interval;
    return;
}

#define METRIC_STATISTIC_NAME "nginx_statistic"
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
                "|%s|%s|%s|%s|%s|%u|%u|\n",
                METRIC_STATISTIC_NAME,
                cip_str,
                ngxip_str,
                nk.sip_str,
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

int attach_l4_probe(struct nginx_probe_bpf *skel)
{
    int err;
    long offset;
    char bin_file_path[BIN_FILE_PATH_LEN] = {0};

    offset = get_func_offset("nginx", "ngx_stream_proxy_init_upstream", bin_file_path);
    if (offset <= 0) {
        printf("Failed to get func(ngx_stream_proxy_init_upstream) offset.\n");
        return 0;
    }

    /* Attach tracepoint handler */
    skel->links.ngx_stream_proxy_init_upstream_probe = bpf_program__attach_uprobe(
        skel->progs.ngx_stream_proxy_init_upstream_probe, false /* not uretprobe */, -1, bin_file_path, offset);
    err = libbpf_get_error(skel->links.ngx_stream_proxy_init_upstream_probe);
    if (err) {
        fprintf(stderr, "Failed to attach uprobe: %d\n", err);
        return 0;
    }

    /* Attach tracepoint handler */
    skel->links.ngx_stream_proxy_init_upstream_retprobe = bpf_program__attach_uprobe(
        skel->progs.ngx_stream_proxy_init_upstream_retprobe, true /* uretprobe */, -1, bin_file_path, offset);
    err = libbpf_get_error(skel->links.ngx_stream_proxy_init_upstream_retprobe);
    if (err) {
        fprintf(stderr, "Failed to attach uprobe: %d\n", err);
        return 0;
    }
    return 1;
}

int attach_l7_probe(struct nginx_probe_bpf *skel)
{
    int err;
    long offset;
    char bin_file_path[BIN_FILE_PATH_LEN] = {0};

    offset = get_func_offset("nginx", "ngx_http_upstream_handler", bin_file_path);
    if (offset <= 0) {
        printf("Failed to get func(ngx_http_upstream_handler) offset.\n");
        return 0;
    }

    skel->links.ngx_http_upstream_handler_probe =
        bpf_program__attach_uprobe(skel->progs.ngx_http_upstream_handler_probe, false, -1, bin_file_path, offset);
    err = libbpf_get_error(skel->links.ngx_http_upstream_handler_probe);
    if (err) {
        fprintf(stderr, "Failed to attach uprobe: %d\n", err);
        return 0;
    }
    return 1;
}

int attach_close_probe(struct nginx_probe_bpf *skel)
{
    int err;
    long offset;
    char bin_file_path[BIN_FILE_PATH_LEN] = {0};

    offset = get_func_offset("nginx", "ngx_close_connection", bin_file_path);
    if (offset <= 0) {
        printf("Failed to get ngx_close_connection func offset.\n");
        return 0;
    }

    skel->links.ngx_close_connection_probe =
        bpf_program__attach_uprobe(skel->progs.ngx_close_connection_probe, false, -1, bin_file_path, offset);
    err = libbpf_get_error(skel->links.ngx_close_connection_probe);
    if (err) {
        printf("Failed to attach uprobe: %d\n", err);
        return 0;
    }
    return 1;
}

int main(int argc, char **argv)
{
    int ret;
    int map_fd = -1;
    struct nginx_probe_bpf *skel;

    ret = args_parse(argc, argv, "t:", ngxprobe_arg_parse);
    if (ret != 0) {
        return -1;
    }

    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

    /* Bump RLIMIT_MEMLOCK to allow BPF sub-system to do anything */
    bump_memlock_rlimit();

    /* Clean handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Load and verify BPF application */
    skel = nginx_probe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton\n");
        return 1;
    }

    ret |= attach_l4_probe(skel);
    ret |= attach_l7_probe(skel);
    if (ret == 0) {
        goto cleanup;
    }

    ret = attach_close_probe(skel);
    if (ret == 0) {
        goto cleanup;
    }

    /* create ngx statistic map_fd */
    map_fd = bpf_create_map(
        BPF_MAP_TYPE_HASH, sizeof(struct ngx_statistic_key), sizeof(struct ngx_statistic), STATISTIC_MAX_ENTRIES, 0);
    if (map_fd < 0) {
        printf("Failed to create statistic map fd.\n");
        goto cleanup;
    }

    printf("Successfully started!\n");

    /* try to hit probe info */
    while (!exiting) {
        pull_probe_data(bpf_map__fd(skel->maps.hs), map_fd);
        print_statistic_map(map_fd);
        sleep(g_print_interval_sec);
    }

cleanup:
    if (map_fd > 0) {
        close(map_fd);
    }
    nginx_probe_bpf__destroy(skel);
    return ret <= 0 ? -1 : 0;
}
