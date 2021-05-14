#ifndef __TCPPROBE__H
#define __TCPPROBE__H

#define AF_INET 2
#define AF_INET6 10

#define INET_ADDRSTRLEN (16)
#define INET6_ADDRSTRLEN (48)

#define TM_STR_LEN  48

#define TCP_ESTABLISHED 1
#define TCP_SYN_SENT 2
#define TCP_SYN_RECV 3
#define TCP_FIN_WAIT1 4
#define TCP_FIN_WAIT2 5
#define TCP_TIME_WAIT 6
#define TCP_CLOSE 7
#define TCP_CLOSE_WAIT 8
#define TCP_LAST_ACK 9
#define TCP_LISTEN 10
#define TCP_CLOSING 11
#define TCP_NEW_SYN_RECV 12
#define TCP_MAX_STATES 13

#define METRIC_MAX_ENTRIES 1000
#define LINK_MAX_ENTRIES 10000

#define LINK_ROLE_SERVER 0
#define LINK_ROLE_CLIENT 1

#define IP6_LEN 16
#define TASK_COMM_LEN 16

#define TCPPROBE_INTERVAL_NS (5000000000)
#define TCPPROBE_CYCLE_SEC (5)

#define MAX_LONG_LINK_FDS_PER_PROC (10)
#define MAX_LONG_LINK_PROCS (20)
#define MAX_PORT_VAL (0xff)

struct long_link_info {
    int fds[MAX_LONG_LINK_FDS_PER_PROC];
    __u8 fd_role[MAX_LONG_LINK_FDS_PER_PROC];
    unsigned int cnt;
};

struct ip {
    union {
        __u32 ip4;
        unsigned char ip6[IP6_LEN];
    };
};

struct metric_key {
    struct ip c_ip;
    struct ip s_ip;
    __u16 s_port;
    __u16 proto;
    __u32 pid;
};

struct metric_data {
    char comm[TASK_COMM_LEN];
    __u32 link_num;
    __u64 rx;
    __u64 tx;
    __u32 segs_in;
    __u32 segs_out;
    __u32 total_retrans;
    __u32 lost;
    __u32 srtt;
};

struct proc_info {
    __u32 pid;
    char comm[TASK_COMM_LEN];
    __u64 role : 1;
    __u64 ts : 63;
};

struct link_key {
    union {
        __u32 src_addr;
        unsigned char src_addr6[IP6_LEN];
    };
    union {
        __u32 dst_addr;
        unsigned char dst_addr6[IP6_LEN];
    };
    __u32 family;
    __u16 src_port;
    __u16 dst_port;
};

struct link_data {
    pid_t pid;
    char comm[TASK_COMM_LEN];
    __u16 states; /* established之后的状态合集 */
    __u16 role;   /* 0: server 1: client */
    __u64 rx;
    __u64 tx;
    __u32 segs_in;
    __u32 segs_out;
    __u32 total_retrans;
    __u32 lost;
    __u32 srtt;
    int sk_err;
    int sk_err_soft;
};

#endif
