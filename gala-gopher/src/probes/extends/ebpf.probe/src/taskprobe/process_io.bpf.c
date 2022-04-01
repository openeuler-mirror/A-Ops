/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: luzhihao
 * Create: 2022-02-10
 * Description: Collecting Task I/O Data
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"
#include "task.h"

char g_linsence[] SEC("license") = "GPL";

struct bpf_map_def SEC("maps") process_example = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(int),
    .value_size = sizeof(int),
    .max_entries = 64,
};

KRAWTRACE(oom_score_adj_update, bpf_raw_tracepoint_args)
{
    int pid = (int)ctx->args[0];

    struct task_key key = {.tgid = pid};
    struct task_data *data = (struct task_data *)bpf_map_lookup_elem(&__task_map, &key);
    if (data) {
        __sync_fetch_and_add(&(data->io.p_io_data.task_oom_score_adj), 1);
    }
}
