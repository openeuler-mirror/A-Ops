#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "tcpprobe.h"

char g_linsence[] SEC("license") = "GPL";

#define _(P)                                   \
    ({                                         \
        typeof(P) val;                         \
        bpf_probe_read(&val, sizeof(val), &P); \
        val;                                   \
    })

struct bpf_map_def SEC("maps") long_link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(struct long_link_info),
    .max_entries = MAX_LONG_LINK_PROCS,
};

struct bpf_map_def SEC("maps") link_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct link_key),
    .value_size = sizeof(struct link_data),
    .max_entries = LINK_MAX_ENTRIES,
};

struct bpf_map_def SEC("maps") sock_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct sock *),
    .value_size = sizeof(struct proc_info),
    .max_entries = LINK_MAX_ENTRIES,
};

/* 监听端口列表 */
struct bpf_map_def SEC("maps") listen_port_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(unsigned short),
    .value_size = sizeof(unsigned short),
    .max_entries = MAX_LONG_LINK_FDS_PER_PROC * MAX_LONG_LINK_PROCS,
};

static void bpf_build_link_key(struct link_key *key, struct sock *sk)
{
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

static void bpf_update_link(struct sock *sk, u16 new_state)
{
    struct link_key key = {0};
    struct link_data data = {0};
    struct proc_info *p;
    struct tcp_sock *tcp = (struct tcp_sock *)sk;

    u32 pid = bpf_get_current_pid_tgid() >> 32;

    bpf_build_link_key(&key, sk);

    p = bpf_map_lookup_elem(&sock_map, &sk);
    if (!p) {
        bpf_printk("no find sock:%p, pid:%u\n", &sk, pid);
        return;
    }

    /* update link metric */
    data.rx = _(tcp->bytes_received);
    data.tx = _(tcp->bytes_acked);
    data.segs_in = _(tcp->segs_in);
    data.segs_out = _(tcp->segs_out);
    data.sk_err = _(sk->sk_err);
    data.sk_err_soft = _(sk->sk_err_soft);
    data.states |= (1 << new_state);
    data.srtt = _(tcp->srtt_us) >> 3;
    data.total_retrans = _(tcp->total_retrans);
    data.lost = _(tcp->lost_out);
    data.pid = p->pid;
    data.role = p->role;
    __builtin_memcpy(&data.comm, &p->comm, TASK_COMM_LEN);
    bpf_map_update_elem(&link_map, &key, &data, BPF_ANY);
    return;
}

static void bpf_add_link(struct sock *sk, int role)
{
    long ret;
    struct proc_info proc = {0};

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

    bpf_update_link(sk, TCP_ESTABLISHED);
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
#if 0
    int i;
    for (i = 0; i < MAX_LONG_LINK_FDS_PER_PROC; i++) {
        if (l->cnt <= i)  {
            break;
        }

        struct sock *sk = bpf_get_sock_from_fd(l->fds[i]);
        if (sk) {
            bpf_add_link(sk, l->fd_role[i]);
        }
    }
#endif
    bpf_map_delete_elem(&long_link_map, &pid);
    return;
}

SEC("kretprobe/inet_csk_accept")
void inet_csk_accept_retprobe(struct pt_regs *ctx)
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

SEC("kprobe/tcp_set_state")
void tcp_set_state_probe(struct pt_regs *ctx)
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

    /* 2 update link data */
    bpf_update_link(sk, new_state);

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

static void bpf_update_link_metric(struct pt_regs *ctx)
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

        /* update link metric */
        bpf_update_link(sk, (u16)(_(sk->sk_state)));

        /* update sock map item */
        p->ts = ts;
        bpf_map_update_elem(&sock_map, &sk, p, BPF_ANY);
    }
    return;
}

SEC("kprobe/tcp_sendmsg")
void tcp_sendmsg_probe(struct pt_regs *ctx)
{
    bpf_update_link_metric(ctx);
}

SEC("kprobe/tcp_recvmsg")
void tcp_recvmsg_probe(struct pt_regs *ctx)
{
    bpf_update_link_metric(ctx);
}
