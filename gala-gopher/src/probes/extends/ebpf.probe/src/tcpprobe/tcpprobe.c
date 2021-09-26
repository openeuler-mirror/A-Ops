#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>

#include "tcpprobe.skel.h"
#include "tcpprobe.h"
#include "tcp.h"
#include "util.h"

#define METRIC_NAME_TCP_LINK "tcp_link"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    return vfprintf(stderr, format, args);
}


static volatile sig_atomic_t stop;

static void sig_int(int signo)
{
    stop = 1;
}

void update_link_metric_data(struct metric_data *dd, struct link_data *d)
{
    if (dd->link_num == 0) {
        memcpy(dd->comm, d->comm, TASK_COMM_LEN);
    }

    dd->link_num++;
    dd->rx += d->rx;
    dd->tx += d->tx;

    /*
        metrics_rtt * (metrics_segs_in + metrics_segs_out) + link_rtt * (link_segs_in + link_segs_out)
       _________________________________________________________________________________________________
       
       (metrics_segs_in + metrics_segs_out + link_segs_in + link_segs_out)
    */ 
    if ((d->segs_in + d->segs_out + dd->segs_in + dd->segs_out)) {
        dd->srtt = (dd->srtt * (dd->segs_in + dd->segs_out) + d->srtt * (d->segs_in + d->segs_out)) /
                   (d->segs_in + d->segs_out + dd->segs_in + dd->segs_out);
    } else {
        dd->srtt = 0;
    }
    dd->segs_in += d->segs_in;
    dd->segs_out += d->segs_out;
    dd->total_retrans += d->total_retrans;
    dd->lost += d->lost;
}

int filter_redundant_data(struct link_key *k, struct link_data *d)
{
    /*
        redundant data
        1 port == 0
        2 rx/tx == 0
    */
    if (strstr(d->comm, "sshd") || strstr(d->comm, "broker")) {
        return 1;
    }
    return 0;
}

void update_link_metric_map(struct link_key *k, struct link_data *d, int map_fd)
{
    struct metric_key key = {0};
    struct metric_data data = {0};

    /* Filtering redundant data */
    int ret = filter_redundant_data(k, d);
    if (ret) {
        return;
    }

    /* build key */
    if (d->role == LINK_ROLE_CLIENT) {
        memcpy((char *)&key.c_ip, (char *)&k->src_addr, sizeof(struct ip));
        memcpy((char *)&key.s_ip, (char *)&k->dst_addr, sizeof(struct ip));
        key.s_port = ntohs(k->dst_port);
    } else {
        memcpy((char *)&key.s_ip, (char *)&k->src_addr, sizeof(struct ip));
        memcpy((char *)&key.c_ip, (char *)&k->dst_addr, sizeof(struct ip));
        key.s_port = k->src_port;
    }
    key.proto = k->family;
    key.pid = d->pid;
    data.role = d->role;

    bpf_map_lookup_elem(map_fd, &key, &data);
    update_link_metric_data(&data, d);

    bpf_map_update_elem(map_fd, &key, &data, BPF_ANY);
    return;
}

void pull_probe_data(int map_fd, int metric_map_fd)
{
    int ret;
    struct link_key key = {0};
    struct link_key next_key = {0};
    struct link_data data;
    unsigned char src_ip_str[INET6_ADDRSTRLEN];
    unsigned char dst_ip_str[INET6_ADDRSTRLEN];

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &data);
        if (ret == 0) {

            ip_str(next_key.family, (unsigned char *)&(next_key.src_addr), src_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.dst_addr), dst_ip_str, INET6_ADDRSTRLEN);
            printf("===[%s:%u]: src_addr:%s:%u, dst_addr:%s:%u, family:%u, role:%s, states:%x, rx:%llu, tx:%llu, "
                   "seg_in:%u, segs_out:%u, total_retrans:%u, lost:%u, srtt:%uus, sk_err:%d, sk_err_soft:%d\n",
                data.comm,
                data.pid,
                src_ip_str,
                next_key.src_port,
                dst_ip_str,
                next_key.dst_port,
                next_key.family,
                (data.role ? "client" : "server"),
                data.states,
                data.rx,
                data.tx,
                data.segs_in,
                data.segs_out,
                data.total_retrans,
                data.lost,
                data.srtt,
                data.sk_err,
                data.sk_err_soft);
            /* 更新link metric */
            update_link_metric_map(&next_key, &data, metric_map_fd);
        }

        if (data.states & (1 << TCP_CLOSE)) {
            bpf_map_delete_elem(map_fd, &next_key);
        } else {
            key = next_key;
        }
    }
    printf("=========\n\n\n\n");
    return;
}

void print_link_metric(int map_fd)
{
    int ret = 0;
    struct metric_key key = {0}, next_key = {0};
    struct metric_data data = {0};

    unsigned char src_ip_str[INET6_ADDRSTRLEN];
    unsigned char dst_ip_str[INET6_ADDRSTRLEN];

    char *tm = get_cur_time();
    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &data);
        if (ret == 0) {
            ip_str(next_key.proto, (unsigned char *)&(next_key.c_ip), src_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.proto, (unsigned char *)&(next_key.s_ip), dst_ip_str, INET6_ADDRSTRLEN);
            fprintf(stdout,
                "|%s|%u|%s|%d|%s|%s|%u|%u|%u|%llu|%llu|%u|%u|%u|%u|%u|\n",
                METRIC_NAME_TCP_LINK,
                next_key.pid,
                data.comm,
                data.role,
                src_ip_str,
                dst_ip_str,
                next_key.s_port,
                next_key.proto,
                data.link_num,
                data.rx,
                data.tx,
                data.segs_in,
                data.segs_out,
                data.total_retrans,
                data.lost,
                data.srtt);

            printf("%s [%u-%s]: c_ip:%s, s_ip:%s:%u, proto:%u, link_num:%u, rx:%llu, tx:%llu, "
                   "segs_in:%u, segs_out:%u, total_retrans:%u, lost:%u, srtt:%uus\n",
                tm,
                next_key.pid,
                data.comm,
                src_ip_str,
                dst_ip_str,
                next_key.s_port,
                next_key.proto,
                data.link_num,
                data.rx,
                data.tx,
                data.segs_in,
                data.segs_out,
                data.total_retrans,
                data.lost,
                data.srtt);
        }

        bpf_map_delete_elem(map_fd, &next_key);
    }
    fflush(stdout);
    return;
}

void bpf_add_long_link_info_to_map(int map_fd, __u32 proc_id, int fd, __u8 role)
{
    struct long_link_info ll = {0};

    bpf_map_lookup_elem(map_fd, &proc_id, &ll);
    ll.fds[ll.cnt] = fd;
    ll.fd_role[ll.cnt] = role;
    ll.cnt++;
    bpf_map_update_elem(map_fd, &proc_id, &ll, BPF_ANY);
}

void bpf_update_long_link_info_to_map(int long_link_map_fd, int listen_port_map_fd) {
    int i, j;
    __u8 role;
    unsigned short listen_port;
    struct tcp_listen_ports* tlps = NULL;
    struct tcp_estabs* tes = NULL;

    tlps = get_listen_ports();
    if (tlps == NULL) {
        goto err;
    }  
    
    /* insert listen ports into map */
    for (i = 0; i < tlps->tlp_num; i++) {
        listen_port = (unsigned short)tlps->tlp[i]->port;
        bpf_map_update_elem(listen_port_map_fd, &listen_port, &listen_port, BPF_ANY);
    }

    tes = get_estab_tcps(tlps);
    if (tes == NULL) {
        goto err;
    }

    /* insert tcp establish into map */
    for (i = 0; i < tes->te_num; i++) {
        role = tes->te[i]->is_client == 1 ? LINK_ROLE_CLIENT : LINK_ROLE_SERVER;
        for (j = 0; j < tes->te[i]->te_comm_num; j++) {
            bpf_add_long_link_info_to_map(long_link_map_fd, 
                (__u32)tes->te[i]->te_comm[j]->pid, (int)tes->te[i]->te_comm[j]->fd, role);
        }
    }

err:
    if (tlps) {
        free_listen_ports(&tlps);
    }
    if (tes) {
        free_estab_tcps(&tes);
    }
    return;
}


/* 输出间隔 xx s */
#define BPF_MAX_OUTPUT_INTERVAL     (3600)
#define BPF_MIN_OUTPUT_INTERVAL     (1)
unsigned int g_output_interval_sec = 5;

void tcpprobe_arg_parse(char opt, char *arg, int idx)
{
    if (opt != 't' || !arg) {
        return;
    }

    unsigned int interval = (unsigned int)atoi(arg);
    if (interval < BPF_MIN_OUTPUT_INTERVAL || interval > BPF_MAX_OUTPUT_INTERVAL) {
        return;
    }
    g_output_interval_sec = interval;
    return;
}
int main(int argc, char **argv)
{
    struct tcpprobe_bpf *skel;
    int err = -1;
    int metric_map_fd = -1;

    err = args_parse(argc, argv, "t:", tcpprobe_arg_parse);
    if (err != 0) {
        return -1;
    }

    printf("arg parse interval time:%us\n", g_output_interval_sec);

    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

	#if UNIT_TESTING
    /* Bump RLIMIT_MEMLOCK  allow BPF sub-system to do anything */
    if (set_memlock_rlimit() == 0) {
		return NULL;
	}
	#endif

    /* Open load and verify BPF application */
    skel = tcpprobe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open BPF skeleton\n");
        return 1;
    }

    /* Attach tracepoint handler */
    err = tcpprobe_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        goto cleanup;
    }

    /* create metric hs map */
    metric_map_fd =
        bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct metric_key), sizeof(struct metric_data), LINK_MAX_ENTRIES, 0);
    if (metric_map_fd < 0) {
        fprintf(stderr, "bpf_create_map metric map fd failed.\n");
        goto cleanup;
    }

    /* update long link info */
    bpf_update_long_link_info_to_map(bpf_map__fd(skel->maps.long_link_map), bpf_map__fd(skel->maps.listen_port_map));

    printf("Successfully started!\n");

    while (!stop) {
        pull_probe_data(bpf_map__fd(skel->maps.link_map), metric_map_fd);
        print_link_metric(metric_map_fd);
        sleep(g_output_interval_sec);
    }

cleanup:
    if (metric_map_fd >= 0) {
        close(metric_map_fd);
    }
    tcpprobe_bpf__destroy(skel);
    return -err;
}
