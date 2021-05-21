#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include <time.h>

#include "tcpprobe.skel.h"
#include "tcpprobe.h"

#define METRIC_NAME_TCP_LINK "tcp_link"

char *get_cur_time()
{
    static char tm[TM_STR_LEN] = {0};
    struct tm *tmp_ptr;
    time_t t;

    time(&t);

    tmp_ptr = localtime(&t);
    snprintf(tm,
        TM_STR_LEN,
        "%d/%d/%d %02d:%02d:%02d",
        (1900 + tmp_ptr->tm_year),
        (1 + tmp_ptr->tm_mon),
        tmp_ptr->tm_mday,
        tmp_ptr->tm_hour,
        tmp_ptr->tm_min,
        tmp_ptr->tm_sec);
    return tm;
}

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

static volatile sig_atomic_t stop;

static void sig_int(int signo)
{
    stop = 1;
}

#define NIP6(addr)                                                                                  \
    ntohs(addr[0]), ntohs(addr[1]), ntohs(addr[2]), ntohs(addr[3]), ntohs(addr[4]), ntohs(addr[5]), \
        (ntohs(addr[6]) >> 8), (ntohs(addr[6]) & 0xff), (ntohs(addr[7]) >> 8), (ntohs(addr[7]) & 0xff)
#define NIP6_FMT "%04x:%04x:%04x:%04x:%04x:%04x:%u.%u.%u.%u"

void ip6_str(unsigned char *ip6, unsigned char *ip_str, unsigned int ip_str_size)
{
    unsigned short *addr = (unsigned short *)ip6;
    snprintf(ip_str, ip_str_size, NIP6_FMT, NIP6(addr));
}
void ip_str(__u32 family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size)
{
    if (family == AF_INET6) {
        (void)ip6_str(ip, ip_str, ip_str_size);
        return;
    }

    snprintf(ip_str, ip_str_size, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    return;
}

int is_valid_ip(unsigned char *ip)
{
    unsigned char i;
    for (i = 0; i < IP6_LEN; i++) {
        if (ip[i]) {
            return 1;
        }
    }
    return 0;
}

void update_link_metric_data(struct metric_data *dd, struct link_data *d)
{
    if (dd->link_num == 0) {
        memcpy(dd->comm, d->comm, TASK_COMM_LEN);
    }

    dd->link_num++;
    dd->rx += d->rx;
    dd->tx += d->tx;
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

void update_link_metric_map(struct link_key *k, struct link_data *d, int map_fd)
{
    struct metric_key key = {0};
    struct metric_data data = {0};

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
                "|%s|%u|%s|%s|%s|%u|%u|%u|%llu|%llu|%u|%u|%u|%u|%u|\n",
                METRIC_NAME_TCP_LINK,
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
    return;
}

#if 1

int bpf_parse_link_buf(char *buf, __u32 *proc_id, int *fd)
{
    char *p = NULL;
    char *pp = buf;
    char *ptr = NULL;

    p = strchr(buf, ',');
    if (!p) {
        return -1;
    }
    if (p) {
        *p = '\0';
        *proc_id = strtol(buf, &ptr, 10);
        buf = p + 1;
    }

    p = strchr(buf, '=');
    if (!p) {
        return -1;
    }

    buf = p + 1;
    p = strchr(buf, ')');
    if (p) {
        *p = '\0';
        *fd = (int)strtol(buf, &ptr, 10);
    }
    return 0;
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

void bpf_add_listen_port_map(int map_fd, char *listen_ports_str)
{
    /* :22|:8088|:8091|:39607 */
    char *s = listen_ports_str;
    char *e = NULL;
    unsigned short port;

    while (*s != '\0') {
        if (*s == ':') {
            e = s + 1;
            port = 0;
            while (*e != '\0' && *e != '|') {
                port = (port * 10) + (*e - '0');
                e++;
            }

            if (port < MAX_PORT_VAL) {
                /* add port */
                bpf_map_update_elem(map_fd, &port, &port, BPF_ANY);
            }
            s = e;
        } else {
            s++;
        }
    }
    return;
}

#define SS_LISTEN_PORT_FMT                                                                                            \
    "ss -anptl | awk '{print $4}' | awk -F ':' '{print $NF}' | sed 's/[^0-9]//g' | sort -n | uniq | xargs | sed 's/ " \
    "/|:/g' | sed 's/^/:/'"
#define SS_ESTAB_WITH_LPORT_FMT \
    "ss -anpt | grep ESTAB | grep -E '%s' | sed '/sshd/d' | sed 's/),(/)\\n(/' | sed 's/.*,pid=//' | sed 's/))/)/'"
#define SS_ESTAB_WITHOUT_LPORT_FMT \
    "ss -anpt | grep ESTAB | grep -Ev '%s' | sed '/sshd/d' | sed 's/),(/)\\n(/' | sed 's/.*,pid=//' | sed 's/))/)/'"
/* 获取环境上的长链接信息：(procId, fd) */
void bpf_update_long_link_info_to_map(int long_link_map_fd, int listen_port_map_fd)
{
#define BUF_STR_LEN 200
    FILE *fp = NULL;
    char cmd[BUF_STR_LEN] = {0};
    char buf[BUF_STR_LEN] = {0};
    char buf1[BUF_STR_LEN] = {0};
    __u32 proc_id;
    int fd = -1;
    int ret;

    fp = popen(SS_LISTEN_PORT_FMT, "r");
    while (fgets(buf, BUF_STR_LEN, fp) != NULL) {
        buf[strlen(buf) - 1] = '\0';
        printf("listen port list:%s\n", buf);
        break;
    }
    pclose(fp);

    /* insert listen ports into map */
    bpf_add_listen_port_map(listen_port_map_fd, buf);

    snprintf(cmd, BUF_STR_LEN, SS_ESTAB_WITHOUT_LPORT_FMT, buf);
    fp = popen(cmd, "r");
    while (fgets(buf1, BUF_STR_LEN, fp) != NULL) {
        ret = bpf_parse_link_buf(buf1, &proc_id, &fd);
        if (ret == 0) {
            bpf_add_long_link_info_to_map(long_link_map_fd, proc_id, fd, LINK_ROLE_CLIENT);
        }
    }
    pclose(fp);

    snprintf(cmd, BUF_STR_LEN, SS_ESTAB_WITH_LPORT_FMT, buf);
    fp = popen(cmd, "r");
    while (fgets(buf1, BUF_STR_LEN, fp) != NULL) {
        ret = bpf_parse_link_buf(buf1, &proc_id, &fd);
        if (ret == 0) {
            bpf_add_long_link_info_to_map(long_link_map_fd, proc_id, fd, LINK_ROLE_SERVER);
        }
    }
    pclose(fp);

    return;
}
#endif

int main(int argc, char **argv)
{
    struct tcpprobe_bpf *skel;
    int err;
    int metric_map_fd = -1;

    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

    /* Bump RLIMIT_MEMLOCK to allow BPF sub-system to do anything */
    bump_memlock_rlimit();

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
        sleep(TCPPROBE_CYCLE_SEC);
    }

cleanup:
    if (metric_map_fd >= 0) {
        close(metric_map_fd);
    }
    tcpprobe_bpf__destroy(skel);
    return -err;
}
