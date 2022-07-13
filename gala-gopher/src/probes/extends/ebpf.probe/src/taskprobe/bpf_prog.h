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
 * Description: bpf load prog
 ******************************************************************************/
#ifndef __BPF_PROG__H
#define __BPF_PROG__H

#pragma once

#include <bpf/libbpf.h>
#include <bpf/bpf.h>

#include "common.h"
#include "args.h"

#define SKEL_MAX_NUM  10
#define TASK_OUTPUT_PATH "/sys/fs/bpf/probe/__taskprobe_task_output"
#define PROC_OUTPUT_PATH "/sys/fs/bpf/probe/__taskprobe_proc_output"
#define PERIOD_PATH "/sys/fs/bpf/probe/__taskprobe_period"
#define TASK_PATH "/sys/fs/bpf/probe/__taskprobe_task"
#define PROC_PATH "/sys/fs/bpf/probe/__taskprobe_proc"

typedef void (*skel_destroy_fn)(void *);

struct __bpf_skel_s {
    skel_destroy_fn fn;
    void *skel;
    void *_link[PATH_NUM];
    size_t _link_num;
};
struct bpf_prog_s {
    struct perf_buffer* pb;
    struct __bpf_skel_s skels[SKEL_MAX_NUM];
    size_t num;
};

static __always_inline void free_bpf_prog(struct bpf_prog_s *prog)
{
    (void)free(prog);
}

static __always_inline struct bpf_prog_s *alloc_bpf_prog(void)
{
    struct bpf_prog_s *prog = malloc(sizeof(struct bpf_prog_s));
    if (prog == NULL) {
        return NULL;
    }

    (void)memset(prog, 0, sizeof(struct bpf_prog_s));
    return prog;
}

static __always_inline void unload_bpf_prog(struct bpf_prog_s **unload_prog)
{
    struct bpf_prog_s *prog = *unload_prog;

    *unload_prog = NULL;
    if (prog == NULL) {
        return;
    }

    for (int i = 0; i < prog->num; i++) {
        if (prog->skels[i].skel) {
            prog->skels[i].fn(prog->skels[i].skel);

            for (int j = 0; j < prog->skels[i]._link_num; j++) {
                if (prog->skels[i]._link[j]) {
                    (void)bpf_link__destroy(prog->skels[i]._link[j]);
                }
            }
        }
    }
    if (prog->pb) {
        perf_buffer__free(prog->pb);
    }
    free_bpf_prog(prog);
    return;
}

struct bpf_prog_s* load_glibc_bpf_prog(struct probe_params *args);
struct bpf_prog_s* load_task_bpf_prog(struct probe_params *args);
struct bpf_prog_s* load_proc_bpf_prog(struct probe_params *args);

#endif
