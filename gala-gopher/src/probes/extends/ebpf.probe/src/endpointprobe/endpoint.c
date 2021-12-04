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

#include "bpf.h"
#include <bpf/bpf.h>
#include "endpoint.skel.h"
#include "endpoint.h"
#include "args.h"

#define OO_NAME "endpoint"
#define INET6_ADDRSTRLEN (48)

static volatile sig_atomic_t stop;
static struct probe_params params = {.period = 5};

static void sig_int(int signo)
{
    stop = 1;
}

static void pull_endpoint_data(int ep_map_fd)
{
    int ret = 0;
    struct endpoint_key_t key = {0}, next_key = {0};
    struct endpoint_val_t data = {0};
    unsigned char s_addr[INET6_ADDRSTRLEN];
    char *time_fmt = get_cur_time();

    while (bpf_map_get_next_key(ep_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(ep_map_fd, &next_key, &data);
        if (ret == 0) {
            if (data.type == SK_TYPE_INIT) {
                key = next_key;
                continue;
            }

            ip_str(data.family, (unsigned char *)&data.s_addr, s_addr, INET6_ADDRSTRLEN);
            fprintf(stdout,
                    "|%s|%d|%s|%d|%u|%d|%d|%d|%s|%u|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|\n",
                    OO_NAME,
                    next_key.pid,
                    data.comm,
                    data.type,
                    data.uid,
                    data.family,
                    data.s_type,
                    data.protocol,
                    s_addr,
                    data.s_port,
                    data.ep_stats.stats[EP_STATS_LISTEN_DROPS],
                    data.ep_stats.stats[EP_STATS_LISTEN_OVERFLOW],
                    data.ep_stats.stats[EP_STATS_PASSIVE_OPENS],
                    data.ep_stats.stats[EP_STATS_ACTIVE_OPENS],
                    data.ep_stats.stats[EP_STATS_ATTEMPT_FAILS],
                    data.ep_stats.stats[EP_STATS_ABORT_CLOSE],
                    data.ep_stats.stats[EP_STATS_REQUEST_FAILS],
                    data.ep_stats.stats[EP_STATS_RMEM_SCHEDULE],
                    data.ep_stats.stats[EP_STATS_TCP_OOM],
                    data.ep_stats.stats[EP_STATS_SEND_TCP_RSTS],
                    data.ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);
            printf("%s [%d-%s] ep_type:%d, ep_uid:%u, ep_family:%d, ep_s_type:%d, ep_protocol:%d, "
                   "ep_addr:%s, ep_port:%u, ep_listen_drops:%lu, ep_listen_overflows:%lu, "
                   "ep_passive_opens:%lu, ep_active_opens:%lu, ep_attempt_fails:%lu, ep_abort_close:%lu, "
                   "ep_request_fails:%lu, ep_rmem_schedule:%lu, ep_tcp_oom:%lu, ep_send_tcp_resets:%lu, "
                   "ep_keepalive_timeout:%lu\n",
                   time_fmt,
                   next_key.pid,
                   data.comm,
                   data.type,
                   data.uid,
                   data.family,
                   data.s_type,
                   data.protocol,
                   s_addr,
                   data.s_port,
                   data.ep_stats.stats[EP_STATS_LISTEN_DROPS],
                   data.ep_stats.stats[EP_STATS_LISTEN_OVERFLOW],
                   data.ep_stats.stats[EP_STATS_PASSIVE_OPENS],
                   data.ep_stats.stats[EP_STATS_ACTIVE_OPENS],
                   data.ep_stats.stats[EP_STATS_ATTEMPT_FAILS],
                   data.ep_stats.stats[EP_STATS_ABORT_CLOSE],
                   data.ep_stats.stats[EP_STATS_REQUEST_FAILS],
                   data.ep_stats.stats[EP_STATS_RMEM_SCHEDULE],
                   data.ep_stats.stats[EP_STATS_TCP_OOM],
                   data.ep_stats.stats[EP_STATS_SEND_TCP_RSTS],
                   data.ep_stats.stats[EP_STATS_KEEPLIVE_TIMEOUT]);
        }
        key = next_key;
    }
    printf("\n\n\n");
    fflush(stdout);
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
    
    LOAD(endpoint);

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "Can't set signal handler: %s\n", strerror(errno));
        goto err;
    }

    printf("Endpoint probe successfully started!\n");

    remove(ep_file_path);
    err = bpf_obj_pin(GET_MAP_FD(endpoint_map), ep_file_path);
    if (err) {
        fprintf(stderr, "Failed to pin endpoint map: %s\n", strerror(errno));
        goto err;
    }
    printf("Endpoint map pin success.\n");

    while (!stop) {
        pull_endpoint_data(GET_MAP_FD(endpoint_map));
        sleep(params.period);
    }

    err = remove(ep_file_path);
    if (!err) {
        printf("Pinned file:(%s) of endpoint map removed.\n", ep_file_path);
    } else {
        fprintf(stderr, "Failed to remove pinned file:(%s) of endpoint map.", ep_file_path);
    }

err:
    UNLOAD(endpoint);
    return -err;
}