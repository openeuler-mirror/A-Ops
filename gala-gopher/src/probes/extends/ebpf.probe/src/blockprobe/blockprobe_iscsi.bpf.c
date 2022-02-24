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

static __always_inline void __calc_iscsi_latency(struct block_data *bdata, struct iscsi_stats *sc_stats, 
                                                                __u64 delta, __u64 ts)
{
    if (delta == 0) {
        return;
    }
    __u64 us = delta >> 3;

    // first calc
    if (bdata->ts == 0) {
        INIT_LATENCY_STATS(sc_stats, latency_iscsi, us);
        bdata->ts = ts;
        return;
    }

    // calculation of intra-period
    if (ts > bdata->ts) {
        if ((ts - bdata->ts) < BLOCKPROBE_INTERVAL_NS) {
            CALC_LATENCY_STATS(sc_stats, latency_iscsi, us);
        } else {
            bdata->ts = ts;  // Start a new statistical period
            INIT_LATENCY_STATS(sc_stats, latency_iscsi, us);
        }
    } else {
        bdata->ts = 0; // error
    }
}

KRAWTRACE(scsi_dispatch_cmd_done, bpf_raw_tracepoint_args)
{
    struct block_key key;
    struct block_data *bdata;
    struct scsi_cmnd *sc = (struct scsi_cmnd *)ctx->args[0];
    struct request* req = _(sc->request);

    get_block_key_by_req(req, &key);
    bdata = get_block_entry(&key);
    if (!bdata) {
        return;
    }
    __u64 ts = bpf_ktime_get_ns();
    __calc_iscsi_latency(bdata, &(bdata->scsi_stats), get_delta_time_ns(req, ts), ts);
}

KRAWTRACE(scsi_dispatch_cmd_timeout, bpf_raw_tracepoint_args)
{
    struct block_key key;
    struct block_data *bdata;
    struct scsi_cmnd *sc = (struct scsi_cmnd *)ctx->args[0];
    struct request* req = _(sc->request);

    get_block_key_by_req(req, &key);
    bdata = get_block_entry(&key);
    if (!bdata) {
        return;
    }
    __sync_fetch_and_add(&(bdata->scsi_stats.count_iscsi_tmout), 1);    
}

KRAWTRACE(scsi_dispatch_cmd_error, bpf_raw_tracepoint_args)
{
    struct block_key key;
    struct block_data *bdata;
    struct scsi_cmnd *sc = (struct scsi_cmnd *)ctx->args[0];
    struct request* req = _(sc->request);

    get_block_key_by_req(req, &key);
    bdata = get_block_entry(&key);
    if (!bdata) {
        return;
    }
    __sync_fetch_and_add(&(bdata->scsi_stats.count_iscsi_err), 1);    
}

