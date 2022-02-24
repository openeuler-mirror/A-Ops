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
 * Create: 2022-02-22
 * Description: block probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif
#define BPF_PROG_KERN
#include "block.h"

char g_linsence[] SEC("license") = "GPL";

static __always_inline void __calc_req_latency(struct block_data *bdata, struct blk_stats *blk_stats, 
                                                                __u64 delta, __u64 ts)
{
    if (delta == 0) {
        return;
    }
    __u64 us = delta >> 3;
    
    // first calc
    if (bdata->ts == 0) {
        INIT_LATENCY_STATS(blk_stats, latency_req, us);
        bdata->ts = ts;
        return;
    }
    
    // calculation of intra-period
    if (ts > bdata->ts) {
        if ((ts - bdata->ts) < BLOCKPROBE_INTERVAL_NS) {
            CALC_LATENCY_STATS(blk_stats, latency_req, us);
        } else {
            bdata->ts = ts;  // Start a new statistical period
            INIT_LATENCY_STATS(blk_stats, latency_req, us);
        }
    } else {
        bdata->ts = 0; // error
    }
}

static __always_inline void __calc_flush_latency(struct block_data *bdata, struct blk_stats *blk_stats, 
                                                                __u64 delta, __u64 ts)
{
    if (delta == 0) {
        return;
    }
    __u64 us = delta >> 3;
    
    // first calc
    if (bdata->ts == 0) {
        INIT_LATENCY_STATS(blk_stats, latency_flush, us);
        bdata->ts = ts;
        return;
    }
    
    // calculation of intra-period
    if (ts > bdata->ts) {
        if ((ts - bdata->ts) < BLOCKPROBE_INTERVAL_NS) {
            CALC_LATENCY_STATS(blk_stats, latency_flush, us);
        } else {
            bdata->ts = ts;  // Start a new statistical period
            INIT_LATENCY_STATS(blk_stats, latency_flush, us);
        }
    } else {
        bdata->ts = 0; // error
    }
}

KPROBE(mq_flush_data_end_io, pt_regs)
{
    struct block_key key;
    struct block_data *bdata;
    struct request *req = (struct request *)PT_REGS_PARM1(ctx);

    get_block_key_by_req(req, &key);
    bdata = get_block_entry(&key);
    if (!bdata) {
        return;
    }
    __u64 ts = bpf_ktime_get_ns();
    __calc_flush_latency(bdata, &(bdata->blk_stats), get_delta_time_ns(req, ts), ts);
}

KPROBE(blk_account_io_done, pt_regs)
{
    struct block_key key;
    struct block_data *bdata;
    struct request *req = (struct request *)PT_REGS_PARM1(ctx);

    get_block_key_by_req(req, &key);
    bdata = get_block_entry(&key);
    if (!bdata) {
        return;
    }
    
    __u64 ts = bpf_ktime_get_ns();
    __calc_req_latency(bdata, &(bdata->blk_stats), get_delta_time_ns(req, ts), ts);
}
