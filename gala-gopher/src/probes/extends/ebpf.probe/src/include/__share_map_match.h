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
#ifndef __SHARE_MAP_MATCH_H__
#define __SHARE_MAP_MATCH_H__

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

struct __probe_key {
    unsigned int smp_id;
    unsigned int pid;
    long bp;
};

#define __PROBE_PARAM1 0
#define __PROBE_PARAM2 1
#define __PROBE_PARAM3 2
#define __PROBE_PARAM4 3
#define __PROBE_PARAM5 4
#define __PROBE_PARAM6 5
#define __PROBE_PARAM_MAX 6
struct __probe_val {
    long params[__PROBE_PARAM_MAX];
};

struct probe_val {
    struct __probe_val val;
};

#define __PROBE_MATCH_MAP_MAX_ENTRIES 1000
struct bpf_map_def SEC("maps") __probe_match_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct __probe_key),
    .value_size = sizeof(struct __probe_val),
    .max_entries = __PROBE_MATCH_MAP_MAX_ENTRIES,
};

static __always_inline __maybe_unused void __get_probe_key(struct __probe_key *key, const long bp) {
    key->smp_id = bpf_get_smp_processor_id();
    key->pid = (unsigned int)bpf_get_current_pid_tgid();
    key->bp = bp;
}

static __always_inline __maybe_unused void __get_probe_val(struct __probe_val *val,
                                                    const long p1,
                                                    const long p2,
                                                    const long p3,
                                                    const long p4,
                                                    const long p5,
                                                    const long p6) {
    val->params[__PROBE_PARAM1] = p1;
    val->params[__PROBE_PARAM2] = p2;
    val->params[__PROBE_PARAM3] = p3;
    val->params[__PROBE_PARAM4] = p4;
    val->params[__PROBE_PARAM5] = p5;
    val->params[__PROBE_PARAM6] = p6;
}

static __always_inline __maybe_unused int __do_push_match_map(const struct __probe_key *key,
                                    const struct __probe_val* val) {
    return bpf_map_update_elem(&__probe_match_map, key, val, BPF_ANY);
}

static __maybe_unused int __do_pop_match_map_entry(const struct __probe_key *key,
                                    struct __probe_val* val)
{
    struct __probe_val* tmp;
    tmp = bpf_map_lookup_elem(&__probe_match_map, (const void *)key);
    if (tmp == 0) {
        return -1;
    }
    val->params[__PROBE_PARAM1] = tmp->params[__PROBE_PARAM1];
    val->params[__PROBE_PARAM2] = tmp->params[__PROBE_PARAM2];
    val->params[__PROBE_PARAM3] = tmp->params[__PROBE_PARAM3];
    val->params[__PROBE_PARAM4] = tmp->params[__PROBE_PARAM4];
    val->params[__PROBE_PARAM5] = tmp->params[__PROBE_PARAM5];
    val->params[__PROBE_PARAM6] = tmp->params[__PROBE_PARAM6];
    return bpf_map_delete_elem(&__probe_match_map, (const void *)key);
}
                                    
#define PROBE_GET_PARMS(func, ctx, probe_val) \
    do { \
        int ret; \
        struct __probe_key __key = {0}; \
        struct __probe_val __val = {0}; \
        __get_probe_key(&__key, (const long)PT_REGS_FP(ctx)); \
        ret = __do_pop_match_map_entry((const struct __probe_key *)&__key, \
                                        &__val); \
        if (ret < 0) { \
            bpf_printk("---PROBE_GET_PARMS[" #func "] pop failed.\n"); \
        } else { \
        __builtin_memcpy(&probe_val.val, &__val, sizeof(struct __probe_val)); \
        } \
        \
    } while (0)
                                    
#define PROBE_PARM1(probe_val) (probe_val).val.params[__PROBE_PARAM1]
#define PROBE_PARM2(probe_val) (probe_val).val.params[__PROBE_PARAM2]
#define PROBE_PARM3(probe_val) (probe_val).val.params[__PROBE_PARAM3]
#define PROBE_PARM4(probe_val) (probe_val).val.params[__PROBE_PARAM4]
#define PROBE_PARM5(probe_val) (probe_val).val.params[__PROBE_PARAM5]
#define PROBE_PARM6(probe_val) (probe_val).val.params[__PROBE_PARAM6]
#endif

#endif
