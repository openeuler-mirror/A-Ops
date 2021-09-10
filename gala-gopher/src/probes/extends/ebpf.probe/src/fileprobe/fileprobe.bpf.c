#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#include "fileprobe.h"

char g_linsence[] SEC("license") = "GPL";
#define _(P)                                   		  \
    ({                                         		  \
        typeof(P) val;                         		  \
        bpf_probe_read_kernel(&val, sizeof(val), &P); \
        val;                                   		  \
    })


struct bpf_map_def SEC("maps") snoop_files_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct snoop_inode),
    .value_size = sizeof(u32),
    .max_entries = SNOOP_FILES_MAX_NUM,
};

struct bpf_map_def SEC("maps") permissions_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct snoop_inode),
    .value_size = sizeof(struct inode_permissions),
    .max_entries = PERMISSION_MAX,
};

struct bpf_map_def SEC("maps") suspicious_op_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct suspicious_op_key),
    .value_size = sizeof(struct suspicious_op_val),
    .max_entries = SUSPICIOUS_MAX,
};

static inline int is_snoop_file(struct file* file, struct snoop_inode* s_inode) {
    u32 *pv;

    /* get inode of file */
    struct inode* inode = _(file->f_inode);
    unsigned long i_inode = _(inode->i_ino);

    s_inode->inode = i_inode;

    pv = bpf_map_lookup_elem(&snoop_files_map, s_inode);
    if (!pv) {
        return 0;
    }
    return 1;
}

SEC("kprobe/vfs_open")
void vfs_open_probe(struct pt_regs *ctx)
{
    struct snoop_inode s_inode;
    struct inode_permissions* permission;
    struct task_struct *task;
    struct file* file = (struct file*)PT_REGS_PARM2(ctx);

    if (!is_snoop_file(file, &s_inode)) {
        return;
    }

    permission = bpf_map_lookup_elem(&permissions_map, &s_inode);
    if (!permission) {
        return;
    }

    task = (struct task_struct *)bpf_get_current_task();
    // TODO: get owner of task
    // FILTER: task
    (void)task;

    if (!(permission->permission & OP_TYPE_READ)) {
        /* suspicious operation */
        struct suspicious_op_key k = {.inode = s_inode.inode,};
        k.ts = (u64)bpf_ktime_get_ns();

        struct suspicious_op_val v = {.op_type = OP_TYPE_READ,};
        v.exe[0] = 0;
        // TODO: fill owner
        
        bpf_map_update_elem(&suspicious_op_map, &k, &v, BPF_ANY);
    }
    return;
}

SEC("kprobe/vfs_write")
void vfs_write_probe(struct pt_regs *ctx)
{
    struct snoop_inode s_inode;
    struct inode_permissions* permission;
    struct task_struct *task;
    struct file* file = (struct file*)PT_REGS_PARM1(ctx);

    if (!is_snoop_file(file, &s_inode)) {
        return;
    }

    permission = bpf_map_lookup_elem(&permissions_map, &s_inode);
    if (!permission) {
        return;
    }

    task = (struct task_struct *)bpf_get_current_task();
    // TODO: get owner of task
    // FILTER: task
    (void)task;

    if (!(permission->permission & OP_TYPE_WRITE)) {
        /* suspicious operation */
        struct suspicious_op_key k = {.inode = s_inode.inode,};
        k.ts = (u64)bpf_ktime_get_ns();

        struct suspicious_op_val v = {.op_type = OP_TYPE_WRITE,};
        v.exe[0] = 0;
        // TODO: fill owner
        
        bpf_map_update_elem(&suspicious_op_map, &k, &v, BPF_ANY);
    }
    return;
}

