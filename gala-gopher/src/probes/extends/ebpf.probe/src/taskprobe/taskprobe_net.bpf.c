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
 * Description: Collecting Task TCP/IP Data
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "bpf.h"

char g_linsence[] SEC("license") = "GPL";

KRAWTRACE(kfree_skb, bpf_raw_tracepoint_args)
{
    u64 addr = (u64)ctx->args[1];

    struct task_key key = {.pid = bpf_get_current_pid_tgid()};
    struct task_data *data = (struct task_data *)bpf_map_lookup_elem(&__task_map, &key);
    if (data) {
        __sync_fetch_and_add(&(data->net.kfree_skb_cnt), 1);
        data->net.kfree_skb_ret_addr = addr;
    }
}
