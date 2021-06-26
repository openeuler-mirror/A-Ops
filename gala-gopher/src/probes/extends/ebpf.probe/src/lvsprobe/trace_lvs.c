#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "trace_lvs.skel.h"
#include "trace_lvs.h"
#include "util.h"

#define METRIC_NAME_LVS_LINK "lvs_link"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    return vfprintf(stderr, format, args);
}

static volatile sig_atomic_t stop;

static void sig_int(int signo)
{
    stop = 1;
}

static void ippro_to_str(unsigned short protocol, unsigned char *type_str)
{
    switch(protocol) {
        case IPPROTO_IP:
            memcpy(type_str, "IP", 16 * sizeof(char));
            break;
        case IPPROTO_TCP:
            memcpy(type_str, "TCP", 16 * sizeof(char));
            break;
        case IPPROTO_UDP:
            memcpy(type_str, "UDP", 16 * sizeof(char));
            break;
        case IPPROTO_IPV6:
            memcpy(type_str, "IPV6", 16 * sizeof(char));
            break;
        default:
            memcpy(type_str, "Err", 16 * sizeof(char));
    }
    return;
}

void update_ipvs_collect_data(struct collect_value *dd)
{
    dd->link_count++;

    return;
}

void update_ipvs_collect_map(struct link_key *k, unsigned short protocol, int map_fd)
{
    struct collect_key      key = {0};
    struct collect_value    val = {0};

    /* build key */
    key.family = k->family;
    memcpy((char *)&key.c_addr, (char *)&k->c_addr, sizeof(struct ip));
    memcpy((char *)&key.v_addr, (char *)&k->v_addr, sizeof(struct ip));
    memcpy((char *)&key.s_addr, (char *)&k->s_addr, sizeof(struct ip));
    key.v_port = k->v_port;
    key.s_port = k->s_port;

    bpf_map_lookup_elem(map_fd, &key, &val);
    update_ipvs_collect_data(&val);
    val.protocol = protocol;
    bpf_map_update_elem(map_fd, &key, &val, BPF_ANY);

    return;
}

static void pull_probe_data(int fd, int collect_fd)
{
    int ret = 0;
    struct link_key   key = {0};
    struct link_key   next_key = {0};
    struct link_value value;
    unsigned char ip_pro_str[16];
    unsigned char cli_ip_str[16];
    unsigned char vir_ip_str[16];
    unsigned char src_ip_str[16];

    while (bpf_map_get_next_key(fd, &key, &next_key) == 0) {
        ret = bpf_map_lookup_elem(fd, &next_key, &value);
        if (ret == 0) {
            ippro_to_str(value.protocol, ip_pro_str);
            ip_str(next_key.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.v_addr), vir_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.s_addr), src_ip_str, INET6_ADDRSTRLEN);
            printf("LVS new connect protocol[%s] type[%s] c[%s:%d]--v[%s:%d]--s[%s:%d] state[%d]. \n",
                ip_pro_str,
                (next_key.family == AF_INET) ? "IPv4" : "IPv6",
                cli_ip_str,
                ntohs(next_key.c_port),
                vir_ip_str,
                ntohs(next_key.v_port),
                src_ip_str,
                ntohs(next_key.s_port),
                value.state);
            /* update collect map */
            update_ipvs_collect_map(&next_key, value.protocol, collect_fd);
        }
        if (value.state == IP_VS_TCP_S_CLOSE) {
            bpf_map_delete_elem(fd, &next_key);
        } else {
            key = next_key;
        }
        
    }
}

void print_ipvs_collect(int map_fd)
{
    int ret = 0;
    struct collect_key  key = {0};
    struct collect_key  next_key = {0};
    struct collect_value    value = {0};

    unsigned char cli_ip_str[16];
    unsigned char vir_ip_str[16];
    unsigned char src_ip_str[16];

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &value);
        if (ret == 0) {
            ip_str(next_key.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.v_addr), vir_ip_str, INET6_ADDRSTRLEN);
            ip_str(next_key.family, (unsigned char *)&(next_key.s_addr), src_ip_str, INET6_ADDRSTRLEN);
            fprintf(stdout,
                "|%s|%s|%s|%s|%u|%u|%u|%llu|\n",
                METRIC_NAME_LVS_LINK,
                cli_ip_str,
                vir_ip_str,
                src_ip_str,
                ntohs(next_key.v_port),
                ntohs(next_key.s_port),
                value.protocol,
                value.link_count);

            printf("collect c_ip[%s], v_ip[%s:%d] s_ip[%s:%d] link_count[%lld]. \n", 
                cli_ip_str,
                vir_ip_str,
                ntohs(next_key.v_port),
                src_ip_str,
                ntohs(next_key.s_port),
                value.link_count);
        }
        bpf_map_delete_elem(map_fd, &next_key);
    }
    fflush(stdout);
    return;
}

int main(int argc, char **argv)
{
    struct trace_lvs_bpf *skel;
    int err = -1;
    int collect_map_fd = -1;
    
    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

	#if UNIT_TESTING
    /* Bump RLIMIT_MEMLOCK  allow BPF sub-system to do anything */
    if (set_memlock_rlimit() == 0) {
		return NULL;
	}
	#endif

    /* Open load and verify BPF application */
    skel = trace_lvs_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open BPF skeleton\n");
        return 1;
    }

    /* Attach tracepoint handler */
    err = trace_lvs_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        goto cleanup;
    }

    /* create collect hash map */
    collect_map_fd = 
        bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct collect_key), sizeof(struct collect_value), 8192, 0);
    if (collect_map_fd < 0) {
        fprintf(stderr, "bpf_create_map collect map fd failed.\n");
        goto cleanup;
    }

    printf("Successfully started! \n");
    
    while (!stop) {
        pull_probe_data(bpf_map__fd(skel->maps.lvs_link_map), collect_map_fd);
        print_ipvs_collect(collect_map_fd);
        sleep(5);
    }

cleanup:
    trace_lvs_bpf__destroy(skel);
    return -err;
}
