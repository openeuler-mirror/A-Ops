#ifndef __EXT_DEF_H__
#define __EXT_DEF_H__
#if 1
#define sk_dontcopy_begin       __sk_common.skc_dontcopy_begin
#define sk_dontcopy_end         __sk_common.skc_dontcopy_end
#define sk_hash                 __sk_common.skc_hash
#define sk_portpair             __sk_common.skc_portpair
#define sk_num                  __sk_common.skc_num
#define sk_dport                __sk_common.skc_dport
#define sk_addrpair             __sk_common.skc_addrpair
#define sk_daddr                __sk_common.skc_daddr
#define sk_rcv_saddr            __sk_common.skc_rcv_saddr
#define sk_family               __sk_common.skc_family
#define sk_state                __sk_common.skc_state
#define sk_reuse                __sk_common.skc_reuse
#define sk_reuseport            __sk_common.skc_reuseport
#define sk_ipv6only             __sk_common.skc_ipv6only
#define sk_net_refcnt           __sk_common.skc_net_refcnt
#define sk_bound_dev_if         __sk_common.skc_bound_dev_if
#define sk_bind_node            __sk_common.skc_bind_node
#define sk_prot                 __sk_common.skc_prot
#define sk_net                  __sk_common.skc_net
#define sk_v6_daddr             __sk_common.skc_v6_daddr
#define sk_v6_rcv_saddr __sk_common.skc_v6_rcv_saddr
#define sk_cookie               __sk_common.skc_cookie
#define sk_incoming_cpu         __sk_common.skc_incoming_cpu
#define sk_flags                __sk_common.skc_flags
#define sk_rxhash               __sk_common.skc_rxhash

/* flags for BPF_MAP_UPDATE_ELEM command */
#define BPF_ANY         0 /* create new element or update existing */
#define BPF_NOEXIST     1 /* create new element if it didn't exist */
#define BPF_EXIST       2 /* update existing element */

/* Supported address families. */
#define AF_UNSPEC	0
#define AF_UNIX		1	/* Unix domain sockets 		*/
#define AF_LOCAL	1	/* POSIX name for AF_UNIX	*/
#define AF_INET		2	/* Internet IP Protocol 	*/
#define AF_AX25		3	/* Amateur Radio AX.25 		*/
#define AF_IPX		4	/* Novell IPX 			*/
#define AF_APPLETALK	5	/* AppleTalk DDP 		*/
#define AF_NETROM	6	/* Amateur Radio NET/ROM 	*/
#define AF_BRIDGE	7	/* Multiprotocol bridge 	*/
#define AF_ATMPVC	8	/* ATM PVCs			*/
#define AF_X25		9	/* Reserved for X.25 project 	*/
#define AF_INET6	10	/* IP version 6			*/

struct ip_vs_conn_fnat {
    char        temp1[16];
    u16         cport;
    u16         dport;
    u16         vport;
    u16         lport;
    u16         af;         /* address family */
    union nf_inet_addr  caddr; /* client address */
    union nf_inet_addr  vaddr; /* virtual address */
    union nf_inet_addr  daddr; /* destination address */
    union nf_inet_addr  laddr; /* local address */
    u32         flags;      /* status flags */
    u16         protocol;   /* Which protocol (TCP/UDP) */
    u16         temp2;
    u64         temp3;
    u64         temp4;
    struct timer_list   timer; /* Expiration timer */
};

struct ip_vs_dest_s {
    u8      temp1[16];  /* for the dests in the service */
    u8      temp2[16];  /* for table with all the dests */
    u16     af;         /* address family */
    u16     port;       /* port number of the server */
    union nf_inet_addr addr; /* IP address of the server */
    u32     flags;      /* dest status flags */
    atomic_t    conn_flags;  /* flags to copy to conn */
};

#endif
#endif
