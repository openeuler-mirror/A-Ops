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
 * Description: thread probe
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
#include "task.h"
#include "thread_io.skel.h"
#include "cpu.skel.h"
#include "bpf_prog.h"

#ifdef OO_NAME
#undef OO_NAME
#endif
#define OO_NAME  "thread"

#define __LOAD_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, g_task_output, TASK_OUTPUT_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, period_map, PERIOD_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, g_task_map, TASK_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static void output_task_metrics(void *ctx, int cpu, void *data, __u32 size)
{
    struct task_data *value = (struct task_data *)data;

    (void)fprintf(stdout,
        "|%s|%d|%d|%s|%llu|%llu|%llu|%u|%u|%llu|%u|\n",
        OO_NAME,
        value->id.pid,
        value->id.tgid,
        value->id.comm,
        value->io.bio_bytes_read,
        value->io.bio_bytes_write,
        value->io.iowait_us,
        value->io.hang_count,
        value->io.bio_err_count,
        value->cpu.off_cpu_ns,
        value->cpu.migration_count);

    (void)fflush(stdout);
    return;
}

struct bpf_prog_s* load_task_bpf_prog(struct probe_params *args)
{
    struct bpf_prog_s *prog;
    struct perf_buffer *pb;

    prog = alloc_bpf_prog();
    if (prog == NULL) {
        return NULL;
    }

    __LOAD_PROBE(thread_io, err2, 1);
    prog->skels[prog->num].skel = thread_io_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)thread_io_bpf__destroy;
    prog->num++;

    __LOAD_PROBE(cpu, err, 1);
    prog->skels[prog->num].skel = cpu_skel;
    prog->skels[prog->num].fn = (skel_destroy_fn)cpu_bpf__destroy;
    prog->num++;

    int out_put_fd = GET_MAP_FD(thread_io, g_task_output);
    pb = create_pref_buffer(out_put_fd, output_task_metrics);
    if (pb == NULL) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    prog->pb = pb;
    return prog;

err:
    UNLOAD(cpu);
err2:
    UNLOAD(thread_io);

    if (prog) {
        free_bpf_prog(prog);
    }
    return NULL;
}

