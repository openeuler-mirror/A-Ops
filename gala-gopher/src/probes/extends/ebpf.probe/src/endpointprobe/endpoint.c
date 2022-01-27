/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 * Description: endpoint_probe user prog
 */
#include <stdio.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>
#include <uthash.h>

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
#define MAX_EXIT_TASK_LEN 4096

static volatile sig_atomic_t stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};

struct exit_task_data {
    int pid;                    /* 用户进程 ID */
    UT_hash_handle hh;
};

static struct exit_task_data *exit_tasks = NULL;
static volatile int latest_pid = 0;

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

static int is_task_deleted(int pid)
{
    struct exit_task_data *tmp;

    HASH_FIND_INT(exit_tasks, &pid, tmp);
    if (tmp != NULL) {
        return 1;
    }

    return 0;
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
            if (is_task_deleted(data.pid)) {
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

static void pull_client_endpoint_data(int c_ep_map_fd)
{
    int ret = 0;
    struct c_endpoint_key_t key = {0};
    struct c_endpoint_key_t next_key = {0};
    struct endpoint_val_t data = {0};

    while (bpf_map_get_next_key(c_ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(c_ep_map_fd, &next_key, &data);
        if (ret == 0) {
            if (is_task_deleted(data.pid)) {
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

static void handle_task_exit_event(void *ctx, int cpu, void *data, unsigned int data_sz)
{
    struct exit_task_data *tmp;
    int pid = *((int*)data);

    HASH_FIND_INT(exit_tasks, &pid, tmp);
    if (tmp == NULL) {
        if (HASH_COUNT(exit_tasks) >= MAX_EXIT_TASK_LEN) {
            printf("Warn: exit task map full, new event dropped.\n");
            return;
        }

        tmp = malloc(sizeof(struct exit_task_data));
        tmp->pid = pid;
        HASH_ADD_INT(exit_tasks, pid, tmp);
        latest_pid = pid;
    }

    return;
}

static void *task_exit_receiver()
{
    int task_exit_fd;
    struct perf_buffer *task_exit_pb;

    task_exit_fd = bpf_obj_get(TASK_EXIT_MAP_FILE_PATH);
    if (task_exit_fd < 0) {
        fprintf(stderr, "Failed to get task exit map.\n");
        stop = 1;
        return NULL;
    }
    task_exit_pb = create_pref_buffer(task_exit_fd, handle_task_exit_event);
    if (task_exit_pb == NULL) {
        fprintf(stderr, "Failed to create perf buffer.\n");
        stop = 1;
        return NULL;
    }

    poll_pb(task_exit_pb, params.period * 1000);

    stop = 1;
    return NULL;
}

static void free_task_data(int end_pid)
{
    struct exit_task_data *cur_task, *tmp;
    int cur_pid;

    HASH_ITER(hh, exit_tasks, cur_task, tmp) {
        HASH_DEL(exit_tasks, cur_task);
        cur_pid = cur_task->pid;
        free(cur_task);
        if (end_pid != 0 && cur_pid == end_pid) {
            break;
        }
    }

    return;
}

int main(int argc, char **argv)
{
    int err = -1;
    int task_exit_fd;
    pthread_t task_thread;
    int end_pid;

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

    err = pthread_create(&task_thread, NULL, task_exit_receiver, NULL);
    if (err != 0) {
        fprintf(stderr, "Failed to create thread.\n");
        goto err;
    }
    printf("Thread of task exit event receiver successfully started!\n");

    while (!stop) {
        task_exit_fd = bpf_obj_get(TASK_EXIT_MAP_FILE_PATH);
        if (task_exit_fd < 0) {
            fprintf(stderr, "Failed to get task exit map.\n");
            goto err;
        }

        end_pid = latest_pid;
        pull_endpoint_data(GET_MAP_FD(s_endpoint_map));
        pull_client_endpoint_data(GET_MAP_FD(c_endpoint_map));
        free_task_data(end_pid);

        sleep(params.period);
    }

err:
    UNLOAD(endpoint);

    if (task_thread > 0) {
        pthread_cancel(task_thread);
    }
    free_task_data(0);

    return -err;
}