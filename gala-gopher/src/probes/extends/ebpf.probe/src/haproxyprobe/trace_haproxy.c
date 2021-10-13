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

#include "trace_haproxy.skel.h"
#include "trace_haproxy.h"
#include "args.h"

#define METRIC_NAME_HAPROXY_LINK "haproxy_link"


static struct probe_params params = {.period = 5};
static volatile bool exiting = false;
static void sig_handler(int sig)
{
    exiting = true;
}

static void get_host_ip(unsigned char *value, unsigned short family)
{
    FILE *fp = NULL;
    char buffer[INET6_ADDRSTRLEN] = {0};
    char cmd[CMD_LEN] = {0};
    int num = -1;

    if (family == AF_INET) {
        snprintf(cmd, CMD_LEN - 1, "ifconfig | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk '{print $2}'");
    } else {
        snprintf(cmd, CMD_LEN - 1, "ifconfig | grep inet6 | grep -v ::1 | awk '{print $2}'");
    }
    
    fp = popen(cmd, "r");
    if (fgets(buffer, 32, fp) == NULL) {
        printf("Fail get_host_ip.\n");
        return ;
    }
    pclose(fp);
    num = sscanf(buffer, "%47s", value);
    if (num < 1) {
        printf("failed get hostip [%d]", errno);
    }
    return ;
}

static void update_collect_count(struct collect_value *dd)
{
    dd->link_count++;

    return;
}

static void update_haproxy_collect_map(struct link_key *k, struct link_value *v, int map_fd)
{
    struct collect_key      key = {0};
    struct collect_value    val = {0};

    /* build key */
    memcpy((char *)&key.c_addr, (char *)&k->c_addr, sizeof(struct ip));
    memcpy((char *)&key.p_addr, (char *)&k->p_addr, sizeof(struct ip));
    memcpy((char *)&key.s_addr, (char *)&k->s_addr, sizeof(struct ip));
    key.p_port = k->p_port;
    key.s_port = k->s_port;
    /* lookup value */
    bpf_map_lookup_elem(map_fd, &key, &val);
    /* update value */
    update_collect_count(&val);
    val.family = v->family;
    val.protocol = v->type;
    val.pid = v->pid;
    /* update hash map */
    bpf_map_update_elem(map_fd, &key, &val, BPF_ANY);

    return;
}

static void pull_probe_data(int fd, int collect_fd)
{
    int ret = 0;
    struct link_key     key = {0};
    struct link_key     next_key = {0};
    struct link_value   value = {0};
    unsigned char cli_ip_str[16];
    unsigned char lb_ip_str[16];
    unsigned char src_ip_str[16];

    while (bpf_map_get_next_key(fd, &key, &next_key) == 0) {
        ret = bpf_map_lookup_elem(fd, &next_key, &value);
        if (ret == 0) {
            ip_str(value.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(value.family, (unsigned char *)&(next_key.p_addr), lb_ip_str, INET6_ADDRSTRLEN);
            ip_str(value.family, (unsigned char *)&(next_key.s_addr), src_ip_str, INET6_ADDRSTRLEN);
	    printf("---- new connect protocol[%s] type[%s] c[%s:%d]--lb[%s:%d]--s[%s:%d] state[%d]. \n",
                (value.type == PR_MODE_TCP) ? "TCP" : "HTTP",
                (value.family == AF_INET) ? "IPv4" : "IPv6",
                cli_ip_str,
                ntohs(next_key.c_port),
                lb_ip_str,
                ntohs(next_key.p_port),
                src_ip_str,
                ntohs(next_key.s_port),
                value.state);
            /* update collect map */
            update_haproxy_collect_map(&next_key, &value, collect_fd);
        }
        if (value.state == SI_ST_CLO) {
            bpf_map_delete_elem(fd, &next_key);
        } else {
            key = next_key;
        }
    }
}

static void print_haproxy_collect(int map_fd)
{
    int ret = 0;
    struct collect_key  key = {0};
    struct collect_key  next_key = {0};
    struct collect_value    value = {0};
    unsigned char cli_ip_str[16];
    unsigned char lb_ip_str[16];
    unsigned char src_ip_str[16];

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &next_key, &value);
        if (ret == 0) {
            ip_str(value.family, (unsigned char *)&(next_key.c_addr), cli_ip_str, INET6_ADDRSTRLEN);
            ip_str(value.family, (unsigned char *)&(next_key.p_addr), lb_ip_str, INET6_ADDRSTRLEN);
            ip_str(value.family, (unsigned char *)&(next_key.s_addr), src_ip_str, INET6_ADDRSTRLEN);
	    fprintf(stdout,
                "|%s|%s|%s|%s|%u|%u|%u|%llu|\n",
                METRIC_NAME_HAPROXY_LINK,
                cli_ip_str,
                lb_ip_str,
                src_ip_str,
                ntohs(next_key.p_port),
                ntohs(next_key.s_port),
                value.protocol,
                value.link_count);
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

	LOAD(trace_haproxy);

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

	UBPF_ATTACH(trace_haproxy, haproxy, back_establish);
	UBPF_ATTACH(trace_haproxy, haproxy, stream_free);

    /* create collect hash map */
    collect_map_fd = 
        bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct collect_key), sizeof(struct collect_value), 8192, 0);
    if (collect_map_fd < 0) {
        fprintf(stderr, "Haproxy Failed to create map.\n");
        goto err;
    }
    
    while (!exiting) {
        pull_probe_data(GET_MAP_FD(haproxy_link_map), collect_map_fd);
        print_haproxy_collect(collect_map_fd);
        sleep(params.period);
    }

err:
/* Clean up */
    UNLOAD(trace_haproxy);
    return 0;
}
