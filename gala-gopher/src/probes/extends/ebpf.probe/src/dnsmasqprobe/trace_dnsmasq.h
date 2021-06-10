#ifndef __TRACE_DNSMASQ__H
#define __TRACE_DNSMASQ__H

#define AF_INET     2   /* Internet IP Protocol */
#define AF_INET6    10  /* IP version 6 */

#define IP6_LEN         16
#define TASK_COMM_LEN   16

#define INET_ADDRSTRLEN     16
#define INET6_ADDRSTRLEN    48
#define MAXDNAME            128 /* maximum presentation domain name */
#define LINK_MAX_ENTRIES    81920

#define F_FORWARD   (1u<<3)
#define F_SERVER    (1u<<18)
#define F_QUERY     (1u<<19)

struct sockaddr {
    unsigned short  sa_family;
    char            sa_data[14];
};

struct sockaddr_in {
    unsigned short  sin_family;
    unsigned short  sin_port;
    unsigned int    sin4_addr;
    unsigned char   pad[8];
};

struct sockaddr_in6 {
    unsigned short  sin_family;
    unsigned short  sin_port;
    unsigned int    sin_flowinfo;
    unsigned char   sin6_addr[IP6_LEN];
    unsigned int    sin6_scope_id;
};

union mysockaddr {
    struct sockaddr     sa;
    struct sockaddr_in  in;
    struct sockaddr_in6 in6;
};

union all_addr {
    unsigned int    addr4;
    unsigned char   addr6[IP6_LEN];
};

struct ip {
    union {
        unsigned int    ip4;
        unsigned char   ip6[IP6_LEN];
    };
};

struct server {
    union mysockaddr    addr;
    union mysockaddr    source_addr;
    char                interface[20];
    unsigned int        ifindex;
    //char                temp[64];
};

struct frec {
    char            temp1[72];
    struct server   *sentto;
    //char          temp2[304];
};

struct link_key {
    struct ip       c_addr;
    struct ip       dns_addr;
    unsigned short  c_port;
    unsigned short  family;
};

struct link_value {
    unsigned int    pid;
    char            comm[TASK_COMM_LEN];
    char            dname[MAXDNAME];
};

struct collect_key {
    struct ip       c_addr;
    struct ip       dns_addr;
    unsigned short  family;
};

struct collect_value {
    unsigned int    link_count;
    unsigned int    pid;
    char            comm[TASK_COMM_LEN];
};

#endif /* __TRACE_DNSMASQ__H */