#ifndef KERNEL_4_19_90_2003_4_0_0036_OE1_H
#define KERNEL_4_19_90_2003_4_0_0036_OE1_H

typedef int pid_t;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef signed char s8;
typedef short s16;
typedef int s32;
typedef long long s64;

#define INET_ADDRSTRLEN (16)
#define INET6_ADDRSTRLEN (48)

#define AF_UNSPEC 0
#define AF_UNIX 1      /* Unix domain sockets 		*/
#define AF_LOCAL 1     /* POSIX name for AF_UNIX	*/
#define AF_INET 2      /* Internet IP Protocol 	*/
#define AF_AX25 3      /* Amateur Radio AX.25 		*/
#define AF_IPX 4       /* Novell IPX 			*/
#define AF_APPLETALK 5 /* AppleTalk DDP 		*/
#define AF_NETROM 6    /* Amateur Radio NET/ROM 	*/
#define AF_BRIDGE 7    /* Multiprotocol bridge 	*/
#define AF_ATMPVC 8    /* ATM PVCs			*/
#define AF_X25 9       /* Reserved for X.25 project 	*/
#define AF_INET6 10    /* IP version 6			*/

enum {
    TCP_ESTABLISHED = 1,
    TCP_SYN_SENT,
    TCP_SYN_RECV,
    TCP_FIN_WAIT1,
    TCP_FIN_WAIT2,
    TCP_TIME_WAIT,
    TCP_CLOSE,
    TCP_CLOSE_WAIT,
    TCP_LAST_ACK,
    TCP_LISTEN,
    TCP_CLOSING, /* Now a valid state */
    TCP_NEW_SYN_RECV,

    TCP_MAX_STATES /* Leave at the end! */
};

struct sock_common {   /* 136 */
    u32 skc_daddr;     /* 0 */
    u32 skc_rcv_saddr; /* 4 */
    union {
        unsigned int skc_hash;
        u16 skc_u16hashes[2];
    };
    /* skc_dport && skc_num must be grouped as well */
    union {
        u32 skc_portpair;
        struct {
            /* 本地端口，使用时需要 ntohs(dport) */
            u16 skc_dport; /* 12 */
                           /* 对端端口 */
            u16 skc_num;   /* 14 */
        };
    };

    unsigned short skc_family; /* 16 */
    volatile unsigned char skc_state;
    unsigned char skc_reuse : 4;
    unsigned char skc_reuseport : 1;
    unsigned char skc_ipv6only : 1;
    unsigned char skc_net_refcnt : 1;

    char tmp0[36];

    unsigned char skc_v6_daddr[16];     /* 56 */
    unsigned char skc_v6_rcv_saddr[16]; /* 72 */
    char tmp[48];
};

struct sock {                       /* 888 */
    struct sock_common __sk_common; /* 0 */
#define sk_num __sk_common.skc_num
#define sk_dport __sk_common.skc_dport
#define sk_daddr __sk_common.skc_daddr
#define sk_rcv_saddr __sk_common.skc_rcv_saddr
#define sk_family __sk_common.skc_family
#define sk_state __sk_common.skc_state
#define sk_v6_daddr __sk_common.skc_v6_daddr
#define sk_v6_rcv_saddr __sk_common.skc_v6_rcv_saddr
    char tmp[432];   /* 136 */
    int sk_err,      /* 568 */
        sk_err_soft; /* 572 */
    char tmp1[312];
};

struct minmax_sample {
    u32 t; /* time measurement was taken */
    u32 v; /* value measured */
};

/* State for the parameterized min-max tracker */
struct minmax {
    struct minmax_sample s[3];
};

struct tcp_options_received {
    /*	PAWS/RTTM data	*/
    long ts_recent_stamp; /* Time we stored ts_recent (for aging) */
    u32 ts_recent;        /* Time stamp to echo next		*/
    u32 rcv_tsval;        /* Time stamp value             	*/
    u32 rcv_tsecr;        /* Time stamp echo reply        	*/
    u16 saw_tstamp : 1,   /* Saw TIMESTAMP on last packet		*/
        tstamp_ok : 1,    /* TIMESTAMP seen on SYN packet		*/
        dsack : 1,        /* D-SACK is scheduled			*/
        wscale_ok : 1,    /* Wscale seen on SYN packet		*/
        sack_ok : 3,      /* SACK seen on SYN packet		*/
        smc_ok : 1,       /* SMC seen on SYN packet		*/
        snd_wscale : 4,   /* Window scaling received from sender	*/
        rcv_wscale : 4;   /* Window scaling to send to receiver	*/
    u8 num_sacks;         /* Number of SACK blocks		*/
    u16 user_mss;         /* mss requested by user in ioctl	*/
    u16 mss_clamp;        /* Maximal mss, negotiated at connection setup */
};

struct tcp_sock { /* 2400 -- 2384 */
    char tmp0[1584];
    u64 bytes_received; /* 1584 RFC4898 tcpEStatsAppHCThruOctetsReceived
                         * sum(delta(rcv_nxt)), or how many bytes
                         * were acked.
                         */
    u32 segs_in;        /* 1592 RFC4898 tcpEStatsPerfSegsIn
                         * total number of segments in.
                         */
    u32 data_segs_in;   /* RFC4898 tcpEStatsPerfDataSegsIn
                         * total number of data segments in.
                         */
    u32 rcv_nxt;        /* What we want to receive next 	*/
    u32 copied_seq;     /* Head of yet unread data		*/
    u32 rcv_wup;        /* rcv_nxt on last window update sent	*/
    u32 snd_nxt;        /* Next sequence we send		*/
    u32 segs_out;       /* 1616 RFC4898 tcpEStatsPerfSegsOut
                         * The total number of segments sent.
                         */
    u32 data_segs_out;  /* RFC4898 tcpEStatsPerfDataSegsOut
                         * total number of data segments sent.
                         */
    u64 bytes_sent;     /* RFC4898 tcpEStatsPerfHCDataOctetsOut
                         * total number of data bytes sent.
                         */
    u64 bytes_acked;    /* 1632 RFC4898 tcpEStatsAppHCThruOctetsAcked
                         * sum(delta(snd_una)), or how many bytes
                         * were acked.
                         */

    char tmp1[152];
    u32 srtt_us;     /* smoothed round trip time << 3 in usecs */
    u32 mdev_us;     /* medium deviation			*/
    u32 mdev_max_us; /* maximal mdev for the last rtt period	*/
    u32 rttvar_us;   /* smoothed mdev_max			*/
    u32 rtt_seq;     /* sequence number to update rttvar	*/
    struct minmax rtt_min;

    u32 packets_out;     /* Packets which are "in flight"	*/
    u32 retrans_out;     /* Retransmitted packets out		*/
    u32 max_packets_out; /* max packets_out in last window */
    u32 max_packets_seq; /* right edge of max_packets_out flight */

    u16 urg_data;        /* Saved octet of OOB data and control flags */
    u8 ecn_flags;        /* ECN status bits.			*/
    u8 keepalive_probes; /* num of allowed keep alive probes	*/
    u32 reordering;      /* Packet reordering metric.		*/
    u32 reord_seen;      /* number of data packet reordering events */
    u32 snd_up;          /* Urgent pointer		*/

    /*
     *      Options received (usually on last packet, some only on SYN packets).
     */
    struct tcp_options_received rx_opt;

    /*
     *	Slow start and congestion control (see also Nagle, and Karn & Partridge)
     */
    u32 snd_ssthresh;   /* Slow start size threshold		*/
    u32 snd_cwnd;       /* Sending congestion window		*/
    u32 snd_cwnd_cnt;   /* Linear increase counter		*/
    u32 snd_cwnd_clamp; /* Do not allow snd_cwnd to grow above this */
    u32 snd_cwnd_used;
    u32 snd_cwnd_stamp;
    u32 prior_cwnd;       /* cwnd right before starting loss recovery */
    u32 prr_delivered;    /* Number of newly delivered packets to
                           * receiver in Recovery. */
    u32 prr_out;          /* Total number of pkts sent during Recovery. */
    u32 delivered;        /* Total data packets delivered incl. rexmits */
    u32 delivered_ce;     /* Like the above but only ECE marked packets */
    u32 lost;             /* Total data packets lost incl. rexmits */
    u32 app_limited;      /* limited until "delivered" reaches this val */
    u64 first_tx_mstamp;  /* start of window send phase */
    u64 delivered_mstamp; /* time we reached "delivered" */
    u32 rate_delivered;   /* saved rate sample: packets delivered */
    u32 rate_interval_us; /* saved rate sample: time elapsed */

    u32 rcv_wnd;       /* Current receiver window		*/
    u32 write_seq;     /* Tail(+1) of data held in tcp send buffer */
    u32 notsent_lowat; /* TCP_NOTSENT_LOWAT */
    u32 pushed_seq;    /* Last pushed seq, required to talk to windows */
    u32 lost_out;      /* Lost packets			*/
    u32 sacked_out;    /* 1988 SACK'd packets			*/
    char tmp3[272];
    u32 total_retrans; /* 2264 Total retransmits for entire connection */
    char tmp2[116];
};

struct inode { /* 632 */
    unsigned short i_mode;
    char tmp[630];
};

struct file { /* 256 */
    char tmp[32];
    struct inode *f_inode; /* 32 */
    char tmp1[160];
    void *private_data; /* 200 */
    char tmp2[48];
};

struct fdtable { /* 56 */
    char tmp[8];
    struct file **fd; /* 8 */
    char tmp1[40];
};

struct files_struct { /* 704 */
    char tmp[32];
    struct fdtable *fdt; /* 32 */
    char tmp1[664];
};

struct task_struct { /* 3968 */
    char tmp[1992];
    struct files_struct *files; /* 1992 */
    char tmp1[1968];
};
typedef enum {
    SS_FREE = 0,     /* not allocated		*/
    SS_UNCONNECTED,  /* unconnected to any socket	*/
    SS_CONNECTING,   /* in process of connecting	*/
    SS_CONNECTED,    /* connected to socket		*/
    SS_DISCONNECTING /* in process of disconnecting	*/
} socket_state;

struct socket {
    socket_state state;

    short type;

    unsigned long flags;

    void *wq;

    struct file *file;
    struct sock *sk;
    void *ops;
};
#endif
