#ifndef __ENDPOINT_H__
#define __ENDPOINT_H__

#define MAX_ENDPOINT_LEN (0xffff)
#define MAX_ENDPOINT_STATS_LEN 20
#define TASK_COMM_LEN 16
#define IP6_LEN 16

#define MAX_ENTRIES 8192

static const char *ep_file_path = "/sys/fs/bpf/endpoint";

enum {
    EP_STATS_LISTEN_DROPS = 0,
    EP_STATS_LISTEN_OVERFLOW,
    EP_STATS_ACTIVE_OPENS,
    EP_STATS_PASSIVE_OPENS,
    EP_STATS_ATTEMPT_FAILS,
    EP_STATS_ABORT_CLOSE,
    EP_STATS_REQUEST_FAILS,
    EP_STATS_RMEM_SCHEDULE,
    EP_STATS_CONNTRACK_FAILS,
    EP_STATS_TCP_OOM,
    EP_STATS_KEEPLIVE_TIMEOUT,
    EP_STATS_SEND_TCP_RSTS,
};

struct endpoint_stats {
    unsigned long stats[MAX_ENDPOINT_STATS_LEN];
};

enum endpoint_type {
    SK_TYPE_INIT = 0,
    SK_TYPE_LISTEN_TCP,
    SK_TYPE_LISTEN_UDP,
};

struct ip {
    union {
        unsigned int ip4;               /* IPv4 地址 */
        unsigned char ip6[IP6_LEN];     /* IPv6 地址 */
    };
};

struct endpoint_key_t {
    int pid;                /* 用户进程 ID */
    unsigned long sock_p;   /* socket 地址 */
};

struct endpoint_val_t {
    enum endpoint_type type;    /* endpoint 类型 */
    unsigned int uid;           /* 用户 ID */
    char comm[TASK_COMM_LEN];   /* 进程名 */
    // unsigned int fd;            /* socket 文件描述符 */
    int family;                 /* 地址族 */
    int s_type;                 /* socket 类型 */
    int protocol;               /* 协议族 */
    struct ip s_addr;           /* socket 绑定的地址 */
    unsigned short s_port;      /* socket 绑定的端口号 */
    struct endpoint_stats ep_stats; /* endpoint 观测指标 */
};

#endif