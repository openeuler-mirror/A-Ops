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
 * Author: Mr.lu
 * Create: 2021-09-28
 * Description: bpf header
 ******************************************************************************/
#ifndef __SHARE_MAP_TASK_H__
#define __SHARE_MAP_TASK_H__

#if defined( BPF_PROG_KERN ) || defined( BPF_PROG_USER )

#ifdef BPF_PROG_USER
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#endif

#ifdef BPF_PROG_KERN

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#endif

#include "task.h"


#define __SHARE_MAP_TASK_MAX_ENTRIES 10 * 1024
struct bpf_map_def SEC("maps") __task_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct task_key),
    .value_size = sizeof(struct task_data),
    .max_entries = __SHARE_MAP_TASK_MAX_ENTRIES,
};

static __always_inline char is_task_exist(int pid)
{
	struct task_key key = {.pid = pid};
	
	if (bpf_map_lookup_elem(&__task_map, &key) == (void *)0) {
		return 0;
	}
	return 1;
}

static __always_inline int upd_task_entry(struct task_key* pk, struct task_data* pd)
{
	return bpf_map_update_elem(&__task_map, pk, pd, BPF_ANY);
}

static __always_inline void* get_task_entry(struct task_key* pk)
{
	return bpf_map_lookup_elem(&__task_map, pk);
}

static __always_inline int del_task_entry(struct task_key* pk)
{
	return bpf_map_delete_elem(&__task_map, pk);
}

#endif

#endif
