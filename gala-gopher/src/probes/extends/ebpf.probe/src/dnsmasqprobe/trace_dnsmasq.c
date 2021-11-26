#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "trace_dnsmasq.skel.h"
#include "trace_dnsmasq.h"
#include "args.h"

#define METRIC_NAME_DNSMASQ_LINK    "dnsmasq_link"


static struct probe_params params = {.period = 5};
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


int main(int argc, char **argv)
{
    int err = -1;
    int collect_map_fd = -1;

    err = args_parse(argc, argv, "t:", &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);

	LOAD(trace_dnsmasq);

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
    
    int ret = 0;
    UBPF_ATTACH(trace_dnsmasq, dnsmasq, send_from, ret);
    if (ret == 0) {
        goto err;
    }
 
    /* create collect hash map */
    collect_map_fd = 
        bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct collect_key), sizeof(struct collect_value), 8192, 0);
    
    while (!exiting) {
        pull_probe_data(GET_MAP_FD(dns_query_link_map), collect_map_fd);
        print_dnsmasq_collect(collect_map_fd);
        sleep(params.period);
    }

err:
/* Clean up */
    UNLOAD(trace_dnsmasq);
    return -err;
}
