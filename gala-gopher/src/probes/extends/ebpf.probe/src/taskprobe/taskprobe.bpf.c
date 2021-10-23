#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "taskprobe.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") task_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct task_key),
    .value_size = sizeof(struct task_kdata),
    .max_entries = TASK_MAP_ENTRY_SIZE,
};

KPROBE(wake_up_new_task, pt_regs)
{
    struct task_key ctkey = {0};
    struct task_kdata *ctkd;
    struct task_key ntkey = {0};
    struct task_kdata ntkd = {0};
    struct task_struct *task;

    ctkey.tgid = bpf_get_current_pid_tgid() >> 32;
    ctkey.pid = bpf_get_current_pid_tgid();
    bpf_printk("[TaskProbe|PARENT]: tgid-%d, pid-%d.\n", ctkey.tgid, ctkey.pid);
    ctkd = bpf_map_lookup_elem(&task_map, &ctkey);
    if (ctkd){
        ctkd->fork_count++;
        bpf_map_update_elem(&task_map, &ctkey, ctkd, BPF_ANY);
    }

    task = (struct task_struct *)PT_REGS_PARM1(ctx);
    ntkey.tgid = _(task->tgid);
    ntkey.pid = _(task->pid);
    ntkd.ptid = ctkey.tgid;
    bpf_map_update_elem(&task_map, &ntkey, &ntkd, BPF_ANY);
    bpf_printk("[TaskProbe|CREATE]: tgid-%d, pid-%d.\n", ntkey.tgid, ntkey.pid);
    return;
}

KPROBE(do_exit, pt_regs)
{
    struct task_key tkey = {0};

    tkey.tgid = bpf_get_current_pid_tgid() >> 32;
    tkey.pid = bpf_get_current_pid_tgid();
    bpf_map_delete_elem(&task_map, &tkey);
    bpf_printk("[TaskProbe|DELETE]: tgid-%d, pid-%d.\n", tkey.tgid, tkey.pid);
    return;
}