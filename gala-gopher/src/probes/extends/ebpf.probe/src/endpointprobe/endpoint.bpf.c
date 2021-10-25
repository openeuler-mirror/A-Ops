#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "endpoint.h"

#define BIG_INDIAN_SK_FL_PROTO_SHIFT    16
#define BIG_INDIAN_SK_FL_PROTO_MASK     0x00ff0000
#define LITTLE_INDIAN_SK_FL_PROTO_SHIFT 8
#define LITTLE_INDIAN_SK_FL_PROTO_MASK  0x0000ff00

char LICENSE[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") endpoint_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct endpoint_key_t),
    .value_size = sizeof(struct endpoint_val_t),
    .max_entries = MAX_ENDPOINT_LEN,
};

struct bpf_map_def SEC("maps") socket_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(u32),
    .value_size = sizeof(unsigned long),
    .max_entries = MAX_ENTRIES,
};

static int is_little_endian()
{
    int i = 1;
    return (int)*((char *)&i) == 1;
}

static void add_item_to_sockmap(unsigned long val)
{
    u32 tid = bpf_get_current_pid_tgid();
    bpf_map_update_elem(&socket_map, &tid, &val, BPF_ANY);
    return;
}

static void* get_item_from_sockmap()
{
    u32 tid = bpf_get_current_pid_tgid();
    return bpf_map_lookup_elem(&socket_map, &tid);
}

static void init_ep_key(struct endpoint_key_t *ep_key, unsigned long sock_p)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    ep_key->pid = pid;
    ep_key->sock_p = sock_p;
    return;
}

static void init_ep_val(struct endpoint_val_t *ep_val, struct socket *sock)
{
    struct sock *sk = _(sock->sk);
    unsigned int sk_flags_offset;

    ep_val->type = SK_TYPE_INIT;
    ep_val->uid = bpf_get_current_uid_gid();
    bpf_get_current_comm(&ep_val->comm, sizeof(ep_val->comm));
    ep_val->s_type = _(sock->type);
    ep_val->family = _(sk->sk_family);
    bpf_probe_read(&sk_flags_offset, sizeof(unsigned int), sk->__sk_flags_offset);
    if (is_little_endian()) {
        ep_val->protocol = (sk_flags_offset & LITTLE_INDIAN_SK_FL_PROTO_MASK) >> LITTLE_INDIAN_SK_FL_PROTO_SHIFT;
    } else {
        ep_val->protocol = (sk_flags_offset & BIG_INDIAN_SK_FL_PROTO_MASK) >> BIG_INDIAN_SK_FL_PROTO_SHIFT;
    }
    
    return;
}

KPROBE(__sock_create, pt_regs)
{
    int type = (int)PT_REGS_PARM3(ctx);
    struct socket **res = (struct socket **)PT_REGS_PARM5(ctx);
    int kern = (int)PT_REGS_PARM6(ctx);
    u32 tid = bpf_get_current_pid_tgid();

    if (kern != 0) {
        return;
    }

    if (type != SOCK_STREAM && type != SOCK_DGRAM) {
        return;
    }

    add_item_to_sockmap((unsigned long)res);
    bpf_printk("====[tid=%u]: start creating new socket\n", tid);
    return;
}

KRETPROBE(__sock_create, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket ***sockppp;
    struct socket *sock;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t ep_val = {0};
    u32 tid = bpf_get_current_pid_tgid();
    long err;

    if (ret < 0) {
        goto cleanup;
    }

    sockppp = (struct socket ***)get_item_from_sockmap();
    if (!sockppp) {
        return;
    }
    sock = _(**sockppp);

    init_ep_key(&ep_key, (unsigned long)sock);
    init_ep_val(&ep_val, sock);
    err = bpf_map_update_elem(&endpoint_map, &ep_key, &ep_val, BPF_ANY);
    if (err < 0) {
        bpf_printk("====[tid=%u]: new endpoint update to map failed\n", tid);
        goto cleanup;
    }
    bpf_printk("====[tid=%u]: new endpoint created.\n", tid);

cleanup:
    bpf_map_delete_elem(&socket_map, &tid);
    return;
}

KPROBE(inet_bind, pt_regs)
{
    struct socket *sock = (struct socket*)PT_REGS_PARM1(ctx);
    add_item_to_sockmap((unsigned long)sock);
    bpf_printk("====[tid=%u]: start binding endpoint.\n", (u32)bpf_get_current_pid_tgid());
    return;
}

KRETPROBE(inet_bind, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket **sockpp;
    struct socket *sock;
    struct sock *sk;
    int type;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();

    if (ret != 0) {
        goto cleanup;
    }

    sockpp = (struct socket **)get_item_from_sockmap();
    if (!sockpp) {
        return;
    }
    sock = *sockpp;
    sk = _(sock->sk);

    init_ep_key(&ep_key, (unsigned long)sock);
    ep_val = (struct endpoint_val_t *)bpf_map_lookup_elem(&endpoint_map, &ep_key);
    if (!ep_val) {
        bpf_printk("====[tid=%u]: endpoint can not find.\n", tid);
        goto cleanup;
    }

    struct ip *ip_addr = (struct ip*)&(ep_val->s_addr);
    if (ep_val->family == AF_INET) {
        ip_addr->ip4 = _(sk->sk_rcv_saddr);
    } else if (ep_val->family == AF_INET6) {
        bpf_probe_read(ip_addr->ip6, IP6_LEN, &sk->sk_v6_rcv_saddr);
    }
    ep_val->s_port = _(sk->sk_num);

    type = _(sock->type);
    if (type == SOCK_DGRAM) {
        if (ep_val) {
            ep_val->type = SK_TYPE_LISTEN_UDP;
            bpf_printk("====[tid=%u]: endpoint has been set to udp listening state.\n", tid);
        }
    }
    
cleanup:
    bpf_map_delete_elem(&socket_map, &tid);
    return;
}

KPROBE(inet_listen, pt_regs)
{
    struct socket *sock = (struct socket*)PT_REGS_PARM1(ctx);

    add_item_to_sockmap((unsigned long)sock);
    bpf_printk("====[tid=%u]: start listening endpoint.\n", (u32)bpf_get_current_pid_tgid());
    return;
}

KRETPROBE(inet_listen, pt_regs)
{
    int ret = PT_REGS_RC(ctx);
    struct socket **sockpp;
    struct socket *sock;
    struct endpoint_key_t ep_key = {0};
    struct endpoint_val_t *ep_val;
    u32 tid = bpf_get_current_pid_tgid();
    long err;

    if (ret != 0) {
        goto cleanup;
    }

    sockpp = (struct socket **)get_item_from_sockmap();
    if (!sockpp) {
        return;
    }
    sock = *sockpp;

    init_ep_key(&ep_key, (unsigned long)sock);
    ep_val = (struct endpoint_val_t *)bpf_map_lookup_elem(&endpoint_map, &ep_key);
    if (ep_val) {
        ep_val->type = SK_TYPE_LISTEN_TCP;
        bpf_printk("====[tid=%u]: endpoint has been set to tcp listening state.\n", tid);
    }

cleanup:
    bpf_map_delete_elem(&socket_map, &tid);
    return;
}

KPROBE(__sock_release, pt_regs)
{
    struct socket *sock = (struct socket*)PT_REGS_PARM1(ctx);
    struct endpoint_key_t ep_key = {0};
    u32 tid = bpf_get_current_pid_tgid();
    long err;
    init_ep_key(&ep_key, (unsigned long)sock);
    err = bpf_map_delete_elem(&endpoint_map, &ep_key);
    if (!err) {
        bpf_printk("====[tid=%u]: endpoint has been removed.\n", tid);
    }
    return;
}