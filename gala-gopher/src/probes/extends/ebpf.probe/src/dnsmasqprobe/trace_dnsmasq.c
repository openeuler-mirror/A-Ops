#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "trace_dnsmasq.skel.h"
#include "trace_dnsmasq.h"
#include "util.h"

#define METRIC_NAME_DNSMASQ_LINK    "dnsmasq_link"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    return vfprintf(stderr, format, args);
}

static void bump_memlock_rlimit(void)
{
    struct rlimit rlim_new = {
        .rlim_cur	= RLIM_INFINITY,
        .rlim_max	= RLIM_INFINITY,
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

static void update_collect_map(struct link_key *k, struct link_value *v, int map_fd)
{
    struct collect_key      key = {0};
    struct collect_value    value = {0};

    /* build key */
    memcpy((char *)&key.c_addr, (char *)&k->c_addr, sizeof(struct ip));
    memcpy((char *)&key.dns_addr, (char *)&k->dns_addr, sizeof(struct ip));
    key.family = k->family;

    /* lookup value */
    bpf_map_lookup_elem(map_fd, &key, &value);
    
    /* update value */
    value.link_count++;
    value.pid = v->pid;
    snprintf(value.comm, TASK_COMM_LEN - 1, v->comm);

    /* update hash map */
    bpf_map_update_elem(map_fd, &key, &value, BPF_ANY);

    return;
}

static void pull_probe_data(int fd, int collect_fd)
{
    int ret = 0;
    struct link_key     key = {0};
    struct link_key     next_key = {0};
    struct link_value   value = {0};
    unsigned char cli_ip_str[16];
    unsigned char dns_ip_str[16];

    while (bpf_map_get_next_key(fd, &key, &next_key) == 0) {
        ret = bpf_map_lookup_elem(fd, &next_key, &value);
        if (ret == 0) {
            ip_str(next_key.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.dns_addr), dns_ip_str, INET6_ADDRSTRLEN);
            printf("---- new connect c[%s:%d]--dns[%s:53], pid[%u] comm[%s]. \n",
                cli_ip_str,
                ntohs(next_key.c_port),
                dns_ip_str,
                value.pid,
                value.comm);
            /* update collect map */
            update_collect_map(&next_key, &value, collect_fd);
        }
        bpf_map_delete_elem(fd, &next_key);
        key = next_key;
    }
}

static void print_dnsmasq_collect(int map_fd)
{
    int ret = 0;
    struct collect_key      key = {0};
    struct collect_key      next_key = {0};
    struct collect_value    value = {0};
    unsigned char cli_ip_str[16];
    unsigned char dns_ip_str[16];

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &value);
        if (ret == 0) {
            ip_str(next_key.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.dns_addr), dns_ip_str, INET6_ADDRSTRLEN);
            fprintf(stdout,
                "|%s|%s|%s|%d|%u|%u|%s|\n",
                METRIC_NAME_DNSMASQ_LINK,
                cli_ip_str,
                dns_ip_str,
                next_key.family,
                value.link_count,
                value.pid,
                value.comm);
        }
        bpf_map_delete_elem(map_fd, &next_key);
    }
    fflush(stdout);
    return;
}

/* 输出间隔 xx s */
#define BPF_MAX_OUTPUT_INTERVAL     (3600)
#define BPF_MIN_OUTPUT_INTERVAL     (1)
unsigned int g_output_interval_sec = 5;
void dnsmasqprobe_arg_parse(char opt, char *arg, int idx)
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
    struct trace_dnsmasq_bpf *skel;
    long uprobe_offset = -1;
    int err = -1;
    int collect_map_fd = -1;
    char bin_file_path[256] = {0};

    err = args_parse(argc, argv, "t:", dnsmasqprobe_arg_parse);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", g_output_interval_sec);

    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

    /* Bump RLIMIT_MEMLOCK to allow BPF sub-system to do anything */
    bump_memlock_rlimit();

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Load and verify BPF application */
    skel = trace_dnsmasq_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton\n");
        return 1;
    }

    uprobe_offset = get_func_offset("dnsmasq", "send_from", bin_file_path);
    
    /* Attach tracepoint handler */
    skel->links.dnsmasq_probe_send_from = bpf_program__attach_uprobe(skel->progs.dnsmasq_probe_send_from,
                            false /* not uretprobe */,
                            -1 /* self pid */,
                            bin_file_path,
                            uprobe_offset);
    err = libbpf_get_error(skel->links.dnsmasq_probe_send_from);
    if (err) {
        fprintf(stderr, "Failed to attach uprobe: %d\n", err);
        goto cleanup;
    }

    /* create collect hash map */
    collect_map_fd = 
        bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct collect_key), sizeof(struct collect_value), 8192, 0);
    
    while (!exiting) {
        pull_probe_data(bpf_map__fd(skel->maps.dns_query_link_map), collect_map_fd);
        print_dnsmasq_collect(collect_map_fd);
        sleep(g_output_interval_sec);
    }

cleanup:
/* Clean up */
    trace_dnsmasq_bpf__destroy(skel);
    return -err;
}
