/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 * Description: endpoint_probe user prog
 */
#include <stdio.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include <bpf/bpf.h>
#include "bpf.h"
#include "endpoint.skel.h"
#include "endpoint.h"
#include "args.h"
#include "taskprobe.h"

#define OO_NAME "endpoint"
#define INET6_ADDRSTRLEN (48)
#define ENDPOINT_MAP_FILE_PATH "/sys/fs/bpf/endpoint"

static volatile sig_atomic_t stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};

static void sig_int(int signo)
{
    stop = 1;
}

static void _output_endpoint_data(struct endpoint_val_t *data)
{
    unsigned char s_addr[INET6_ADDRSTRLEN];

    ip_str(data->family, (unsigned char *)&data->s_addr, s_addr, INET6_ADDRSTRLEN);
    fprintf(stdout,
            "|%s|%d|%s|%d|%u|%d|%d|%d|%s|%u|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|\n",
            OO_NAME,
            data->pid,
            data->comm,
            data->type,
            data->uid,
            data->family,
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
            data->ep_stats.stats[EP_STATS_SEND_TCP_RSTS],
            data->ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);

    return;
}

static void _print_endpoint_data(struct endpoint_val_t *data)
{
    unsigned char s_addr[INET6_ADDRSTRLEN];
    char *time_fmt = get_cur_time();

    ip_str(data->family, (unsigned char *)&data->s_addr, s_addr, INET6_ADDRSTRLEN);
    printf("%s [%d-%s] ep_type:%d, ep_uid:%u, ep_family:%d, ep_s_type:%d, ep_protocol:%d, "
            "ep_addr:%s, ep_port:%u, ep_listen_drops:%lu, ep_listen_overflows:%lu, "
            "ep_passive_opens:%lu, ep_active_opens:%lu, ep_attempt_fails:%lu, ep_abort_close:%lu, "
            "ep_request_fails:%lu, ep_rmem_schedule:%lu, ep_tcp_oom:%lu, ep_send_tcp_resets:%lu, "
            "ep_keepalive_timeout:%lu\n",
            time_fmt,
            data->pid,
            data->comm,
            data->type,
            data->uid,
            data->family,
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
            data->ep_stats.stats[EP_STATS_SEND_TCP_RSTS],
            data->ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);

    return;
}

static void pull_endpoint_data(int s_ep_map_fd, int task_map_fd)
{
    int ret = 0;
    struct s_endpoint_key_t key = {0};
    struct s_endpoint_key_t next_key = {0};
    struct endpoint_val_t data = {0};
    struct task_key task_key = {0};
    struct task_kdata task_data = {0};

    while (bpf_map_get_next_key(s_ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(s_ep_map_fd, &next_key, &data);
        if (ret == 0) {
            task_key.tgid = data.pid;
            task_key.pid = data.pid;
            ret = bpf_map_lookup_elem(task_map_fd, &task_key, &task_data);
            if (ret != 0) {
                bpf_map_delete_elem(s_ep_map_fd, &next_key);
                continue;
            }
            _output_endpoint_data(&data);
            _print_endpoint_data(&data);
        }
        key = next_key;
    }

    return;
}

static void pull_client_endpoint_data(int c_ep_map_fd, int task_map_fd)
{
    int ret = 0;
    struct c_endpoint_key_t key = {0};
    struct c_endpoint_key_t next_key = {0};
    struct endpoint_val_t data = {0};
    struct task_key task_key = {0};
    struct task_kdata task_data = {0};

    while (bpf_map_get_next_key(c_ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(c_ep_map_fd, &next_key, &data);
        if (ret == 0) {
            task_key.tgid = next_key.pid;
            task_key.pid = next_key.pid;
            ret = bpf_map_lookup_elem(task_map_fd, &task_key, &task_data);
            if (ret != 0) {
                bpf_map_delete_elem(c_ep_map_fd, &next_key);
                continue;
            }
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
    int task_map_fd;

    err = args_parse(argc, argv, "t:", &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);

    LOAD(endpoint);

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "Can't set signal handler: %d\n", errno);
        goto err;
    }

    printf("Endpoint probe successfully started!\n");

    remove(ENDPOINT_MAP_FILE_PATH);
    err = bpf_obj_pin(GET_MAP_FD(s_endpoint_map), ENDPOINT_MAP_FILE_PATH);
    if (err) {
        fprintf(stderr, "Failed to pin endpoint map: %d\n", errno);
        goto err;
    }
    printf("Endpoint map pin success.\n");

    while (!stop) {
        task_map_fd = bpf_obj_get(TASK_MAP_FILE_PATH);
        if ( task_map_fd < 0) {
            fprintf(stderr, "Failed to get task map: %d\n", errno);
            break;
        }

        pull_endpoint_data(GET_MAP_FD(s_endpoint_map), task_map_fd);
        pull_client_endpoint_data(GET_MAP_FD(c_endpoint_map), task_map_fd);

        sleep(params.period);
    }

    err = remove(ENDPOINT_MAP_FILE_PATH);
    if (!err) {
        printf("Pinned file:(%s) of endpoint map removed.\n", ENDPOINT_MAP_FILE_PATH);
    } else {
        fprintf(stderr, "Failed to remove pinned file:(%s) of endpoint map.", ENDPOINT_MAP_FILE_PATH);
    }

err:
    UNLOAD(endpoint);
    return -err;
}