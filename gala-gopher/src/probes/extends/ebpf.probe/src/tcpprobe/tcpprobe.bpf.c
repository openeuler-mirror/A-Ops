#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "tcpprobe.h"

char g_linsence[] SEC("license") = "GPL";

// Used to identifies the link TCP pid and fd.
// Temporary MAP. Data exists only in the startup phase.
struct bpf_map_def SEC("maps") long_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(struct long_link_info),
    .max_entries = MAX_LONG_LINK_PROCS,
};

// Used to identifies the TCP 5-tuple.
// Should be used for global MAP.
struct bpf_map_def SEC("maps") link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct link_key),
    .value_size = sizeof(struct link_data),
    .max_entries = LINK_MAX_ENTRIES,
};

// Used to identifies the TCP sock object, include PID, COMM, and role of the SOCK object.
// Equivalent to TCP 5-tuple objects.
struct bpf_map_def SEC("maps") sock_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct sock *),
    .value_size = sizeof(struct proc_info),
    .max_entries = LINK_MAX_ENTRIES,
};

// Used to identifies the TCP listen port.
struct bpf_map_def SEC("maps") listen_port_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(unsigned short),
    .value_size = sizeof(unsigned short),
    .max_entries = MAX_LONG_LINK_FDS_PER_PROC * MAX_LONG_LINK_PROCS,
};

static __always_inline void __get_link_key_by_sock(struct link_key *key, struct sock *sk) {
    key->family = _(sk->sk_family);
    if (key->family == AF_INET) {
        key->src_addr = _(sk->sk_rcv_saddr);
        key->dst_addr = _(sk->sk_daddr);
    } else {
        bpf_probe_read_user(key->src_addr6, IP6_LEN, &sk->sk_v6_rcv_saddr);
        bpf_probe_read_user(key->dst_addr6, IP6_LEN, &sk->sk_v6_daddr);
    }

    key->src_port = _(sk->sk_num);
    key->dst_port = _(sk->sk_dport);

    return;
}

static __always_inline struct proc_info *__get_sock_data(struct sock *sk) {
    return bpf_map_lookup_elem(&sock_map, &sk);
}

static __always_inline struct link_data *__get_link_entry_by_sock(struct sock *sk) {
    struct link_key key = {0};
    
    __get_link_key_by_sock(&key, sk);
    
    return bpf_map_lookup_elem(&link_map, &key);
}

static __always_inline void __create_link_entry_by_sock(struct link_key *key, 
                                struct sock *sk, u16 new_state) {
    struct link_data data = {0};
    struct proc_info *p;
    struct tcp_sock *tcp = (struct tcp_sock *)sk;

    u32 pid = bpf_get_current_pid_tgid() >> 32;
    p = __get_sock_data(sk);
    if (!p) {
        bpf_printk("no find sock:%p, pid:%u\n", &sk, pid);
        return;
    }

    TCPPROBE_UPDATE_STATS(data, sk, new_state);
    TCPPROBE_UPDATE_PRCINFO(data, p);
    bpf_map_update_elem(&link_map, key, &data, BPF_ANY);
}

static void __update_link_stats(struct sock *sk, u16 new_state) {
    struct link_data *data;
    struct link_key key = {0};

    __get_link_key_by_sock(&key, sk);
    data = __get_link_entry_by_sock(sk);
    if (!data) {
        __create_link_entry_by_sock(&key, sk, new_state);
        return;
    }
    TCPPROBE_UPDATE_STATS(*data, sk, new_state);
    return;
}

static void update_link_event(struct sock *sk, enum TCPPROBE_EVT_E type) {
    struct link_data *data;
    struct link_key key = {0};
    
    __get_link_key_by_sock(&key, sk);
    data = __get_link_entry_by_sock(sk);
    if (!data) {
        __create_link_entry_by_sock(&key, sk, _(sk->sk_state));
        return;
    }
    TCPPROBE_INC_EVT(type, *data);
    return;
}

static void bpf_add_link(struct sock *sk, int role)
{
    long ret = -1;
    struct proc_info proc = {0};
    u16 src_port = _(sk->sk_num);
    u16 dst_port = _(sk->sk_dport);
    /* if port 0, break. */
    if (dst_port == 0 || src_port == 0) {
        return;
    }

    bpf_get_current_comm(&proc.comm, sizeof(proc.comm));
    if (proc.comm[0] == 's' && proc.comm[1] == 's' && proc.comm[2] == 'h' &&
        (proc.comm[3] == '\0' || (proc.comm[3] == 'd' && proc.comm[4] == '\0'))) {
        /* skip ssh sshd proc */
        return;
    }

    proc.pid = bpf_get_current_pid_tgid() >> 32;
    proc.ts = bpf_ktime_get_ns();
    proc.role = role;

    ret = bpf_map_update_elem(&sock_map, &sk, &proc, BPF_ANY);
    if (ret != 0) {
        bpf_printk("====bpf_add_link failed\n");
        return;
    }

    __update_link_stats(sk, TCP_ESTABLISHED);
    return;
}

static struct sock *bpf_get_sock_from_fd(int fd)
{
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    struct files_struct *files = _(task->files);
    struct fdtable *fdt = _(files->fdt);
    struct file **ff = _(fdt->fd);
    struct file *f;
    bpf_probe_read_kernel(&f, sizeof(struct file *), (struct file *)(ff + fd));
    if (!f) {
        bpf_printk("---bpf_get_sock_from_fd fd:%d failed\n", fd);
        return 0;
    }

    struct inode *fi = _(f->f_inode);
    unsigned short imode = _(fi->i_mode);
    if (((imode & 00170000) != 0140000)) {
        /* not sock fd */
        bpf_printk("---bpf_get_sock_from_fd fd:%d not sock fd\n", fd);
        return 0;
    }

    struct socket *sock = _(f->private_data);
    struct sock *sk = _(sock->sk);
    return sk;
}

static void bpf_add_each_long_link(int fd, int role)
{
    if (fd == 0) {
        return;
    }

    struct sock *sk = bpf_get_sock_from_fd(fd);
    if (sk) {
        bpf_add_link(sk, role);
    }
    return;
}

static void bpf_add_long_link(u32 pid)
{
    struct long_link_info *l = bpf_map_lookup_elem(&long_link_map, &pid);
    if (!l) {
        return;
    }

    bpf_add_each_long_link(l->fds[0], l->fd_role[0]);
    bpf_add_each_long_link(l->fds[1], l->fd_role[1]);
    bpf_add_each_long_link(l->fds[2], l->fd_role[2]);
    bpf_add_each_long_link(l->fds[3], l->fd_role[3]);
    bpf_add_each_long_link(l->fds[4], l->fd_role[4]);
    bpf_add_each_long_link(l->fds[5], l->fd_role[5]);
    bpf_add_each_long_link(l->fds[6], l->fd_role[6]);
    bpf_add_each_long_link(l->fds[7], l->fd_role[7]);
    bpf_add_each_long_link(l->fds[8], l->fd_role[8]);
    bpf_add_each_long_link(l->fds[9], l->fd_role[9]);

    bpf_map_delete_elem(&long_link_map, &pid);
    return;
}

KRETPROBE(inet_csk_accept, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_RC(ctx);
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    char comm[TASK_COMM_LEN] = {0};

    bpf_get_current_comm(&comm, sizeof(comm));

    /* server: add new link */
    bpf_add_link(sk, LINK_ROLE_SERVER);

    /* add long link sock map */
    bpf_add_long_link(pid);
    return;
}

KPROBE(tcp_set_state, pt_regs)
{
    u16 new_state = (u16)PT_REGS_PARM2(ctx);
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct tcp_sock *tcp = (struct tcp_sock *)sk;

    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (new_state == TCP_SYN_SENT) {
        /* client: add new link */
        bpf_add_link(sk, LINK_ROLE_CLIENT);

        /* add long link sock map */
        bpf_add_long_link(pid);
        return;
    }

    if (new_state != TCP_CLOSE) {
        return;
    }

    /* 2 update link stats */
    __update_link_stats(sk, new_state);

    /* 3 del sock_map item */
    bpf_map_delete_elem(&sock_map, &sk);
    return;
}

static inline int bpf_get_sk_role(struct sock *sk)
{
    unsigned short sk_src_port = _(sk->sk_num);
    unsigned short *port = bpf_map_lookup_elem(&listen_port_map, &sk_src_port);
    if (port) {
        return LINK_ROLE_SERVER;
    }
    return LINK_ROLE_CLIENT;
}

// legal data path observation 
static void update_link_stats(struct pt_regs *ctx)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);
    struct proc_info *p = bpf_map_lookup_elem(&sock_map, &sk);
    if (!p) {
        /* long link before bpf detect */
        int role = bpf_get_sk_role(sk);
        bpf_add_link(sk, role);
        return;
    }

    u64 ts = bpf_ktime_get_ns();
    if ((ts - p->ts) > TCPPROBE_INTERVAL_NS) {
        struct tcp_sock *tcp = (struct tcp_sock *)sk;
        u32 pid = bpf_get_current_pid_tgid() >> 32;

        /* update link stats */
        __update_link_stats(sk, (u16)(_(sk->sk_state)));

        /* update sock map item */
        p->ts = ts;
        bpf_map_update_elem(&sock_map, &sk, p, BPF_ANY);
    }
    return;
}

KPROBE(tcp_sendmsg, pt_regs)
{
    update_link_stats(ctx);
}


KPROBE(tcp_recvmsg, pt_regs)
{
    update_link_stats(ctx);
}

KPROBE(tcp_drop, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);

    __update_link_stats(sk, (u16)(_(sk->sk_state)));
}

KPROBE_RET(tcp_add_backlog, pt_regs) {
    bool discard = (bool)PT_REGS_RC(ctx); 
    struct sock *sk;
    struct probe_val val;

    PROBE_GET_PARMS(tcp_add_backlog, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (discard) {
        update_link_event(sk, TCPPROBE_EVT_BACKLOG);
    }
}

KPROBE_RET(tcp_v4_inbound_md5_hash, pt_regs) {
    bool discard = (bool)PT_REGS_RC(ctx); 
    struct sock *sk;
    struct probe_val val;

    PROBE_GET_PARMS(tcp_v4_inbound_md5_hash, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (discard) {
        update_link_event(sk, TCPPROBE_EVT_MD5);
    }
}

KPROBE_RET(tcp_filter, pt_regs) {
    bool discard = (bool)PT_REGS_RC(ctx); 
    struct sock *sk;
    struct probe_val val;

    PROBE_GET_PARMS(tcp_filter, ctx, val);
    sk = (struct sock *)PROBE_PARM1(val);
    if (discard) {
        update_link_event(sk, TCPPROBE_EVT_FILTER);
    }
}

/*
KPROBE(tcp_data_queue_ofo, pt_regs)
{
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);

    update_link_event(sk, TCPPROBE_EVT_OFO);
}
*/

