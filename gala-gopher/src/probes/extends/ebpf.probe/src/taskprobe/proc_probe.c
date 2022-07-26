/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: luzhihao
 * Create: 2022-07-13
 * Description: process probe
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "proc.h"
#include "event.h"
#include "syscall.skel.h"
#include "ex4.skel.h"
#include "overlay.skel.h"
#include "tmpfs.skel.h"
#include "page.skel.h"
#include "bpf_prog.h"

#ifdef OO_NAME
#undef OO_NAME
#endif
#define OO_NAME  "proc"

#define OVERLAY_MOD  "overlay"
#define EXT4_MOD  "ext4"

#define __LOAD_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, period_map, PERIOD_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, g_proc_map, PROC_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, g_proc_output, PROC_OUTPUT_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static void report_proc_metrics(struct proc_data_s *proc)
{
    char entityId[INT_LEN];

    entityId[0] = 0;
    (void)snprintf(entityId, INT_LEN, "%d", proc->proc_id);

    if (proc->syscall.failed > 0) {
        report_logs(OO_NAME,
                    entityId,
                    "syscall_failed",
                    EVT_SEC_WARN,
                    "Process(COMM:%s PID:%u) syscall failed(SysCall-ID:%d RET:%d COUNT:%u).",
                    proc->comm,
                    proc->proc_id,
                    proc->syscall.last_syscall_id,
                    proc->syscall.last_ret_code,
                    proc->syscall.failed);
    }

    if (proc->dns_op.gethostname_failed > 0) {
        report_logs(OO_NAME,
                    entityId,
                    "gethostname_failed",
                    EVT_SEC_WARN,
                    "Process(COMM:%s PID:%u) gethostname failed(COUNT:%u).",
                    proc->comm,
                    proc->proc_id,
                    proc->dns_op.gethostname_failed);
    }
}

static void output_proc_metrics(void *ctx, int cpu, void *data, __u32 size)
{
    struct proc_data_s *proc = (struct proc_data_s *)data;

    report_proc_metrics(proc);

    (void)fprintf(stdout,
        "|%s|%u|%s|"
        "%u|%llu|%llu|%llu|%llu|"
        "%llu|%llu|"
        "%llu|%llu|%llu|%llu|"
        "%llu|%llu|%llu|"
        "%llu|%llu|%llu|%llu|"
        "%llu|%llu|%llu|%llu|"
        "%llu|%llu|%llu|"
        "%llu|%llu|%llu|%llu|%llu|"
        "%llu|%llu|\n",
        OO_NAME,
        proc->proc_id,
        proc->comm,

        proc->syscall.failed,
        proc->syscall.ns_mount,
        proc->syscall.ns_umount,
        proc->syscall.ns_read,
        proc->syscall.ns_write,

        proc->syscall.ns_sendmsg,
        proc->syscall.ns_recvmsg,

        proc->syscall.ns_sched_yield,
        proc->syscall.ns_futex,
        proc->syscall.ns_epoll_wait,
        proc->syscall.ns_epoll_pwait,

        proc->syscall.ns_fork,
        proc->syscall.ns_vfork,
        proc->syscall.ns_clone,

        proc->op_ext4.ns_read,
        proc->op_ext4.ns_write,
        proc->op_ext4.ns_open,
        proc->op_ext4.ns_flush,

        proc->op_overlay.ns_read,
        proc->op_overlay.ns_write,
        proc->op_overlay.ns_open,
        proc->op_overlay.ns_flush,

        proc->op_tmpfs.ns_read,
        proc->op_tmpfs.ns_write,
        proc->op_tmpfs.ns_flush,

        proc->page_op.reclaim_ns,
        proc->page_op.count_access_pagecache,
        proc->page_op.count_mark_buffer_dirty,
        proc->page_op.count_load_page_cache,
        proc->page_op.count_mark_page_dirty,

        proc->dns_op.gethostname_failed,
        proc->dns_op.gethostname_ns);

    (void)fflush(stdout);
    return;
}

struct bpf_prog_s* load_proc_bpf_prog(struct probe_params *args)
{
    struct bpf_prog_s *prog;
    struct perf_buffer *pb;
    char is_load_overlay, is_load_ext4;

    is_load_overlay = is_exist_mod(OVERLAY_MOD);
    is_load_ext4 = is_exist_mod(EXT4_MOD);

    prog = alloc_bpf_prog();
    if (prog == NULL) {
        return NULL;
    }

    __LOAD_PROBE(syscall, err5, 1);
    prog->skels[prog->num].skel = syscall_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)syscall_bpf__destroy;
    prog->num++;

    __LOAD_PROBE(ex4, err4, is_load_ext4);
    prog->skels[prog->num].skel = ex4_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)ex4_bpf__destroy;
    prog->num++;

    __LOAD_PROBE(overlay, err3, is_load_overlay);
    prog->skels[prog->num].skel = overlay_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)overlay_bpf__destroy;
    prog->num++;

    __LOAD_PROBE(tmpfs, err2, 1);
    prog->skels[prog->num].skel = tmpfs_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)tmpfs_bpf__destroy;
    prog->num++;

    __LOAD_PROBE(page, err, 1);
    prog->skels[prog->num].skel = page_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)page_bpf__destroy;
    prog->num++;

    int out_put_fd = GET_MAP_FD(syscall, g_proc_output);
    pb = create_pref_buffer(out_put_fd, output_proc_metrics);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    prog->pb = pb;
    return prog;

err:
    UNLOAD(page);
err2:
    UNLOAD(tmpfs);
err3:
    if (is_load_overlay) {
        UNLOAD(overlay);
    }
err4:
    if (is_load_ext4) {
        UNLOAD(ex4);
    }
err5:
    UNLOAD(syscall);

    if (prog) {
        free_bpf_prog(prog);
    }
    return NULL;
}

