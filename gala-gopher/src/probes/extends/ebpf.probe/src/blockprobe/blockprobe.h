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
#ifndef __BLOCKPROBE__H
#define __BLOCKPROBE__H

enum blk_type_e {
    BLK_TYPE_DISK = 0,
    BLK_TYPE_PART    
};

enum blk_drv_e {
    BLK_DRV_ISCSI = 0,
    BLK_DRV_VIRTIO    
};

struct block_key {
    int major;
    int first_minor;
};

struct blk_stats {
    __u32 latency_req_max;      // FROM delta between'blk_account_io_done' and @req->start_time_ns
    __u32 latency_req_avg;      // Same as above
    __u32 latency_req_last;     // Same as above
    __u32 latency_flush_max;    // FROM delta between 'mq_flush_data_end_io' and @req->start_time_ns
    __u32 latency_flush_avg;    // Same as above
    __u32 latency_flush_last;   // Same as above
};

struct blk_sas_stats {
    __u64 count_sas_abort;      // FROM 'sas_task_abort'
};

// Comply with the kernel definition
#define ISCSI_ERR_BASE          1000
enum iscsi_err {
    ISCSI_OK            = 0,

    ISCSI_ERR_DATASN        = ISCSI_ERR_BASE + 1,
    ISCSI_ERR_DATA_OFFSET       = ISCSI_ERR_BASE + 2,
    ISCSI_ERR_MAX_CMDSN     = ISCSI_ERR_BASE + 3,
    ISCSI_ERR_EXP_CMDSN     = ISCSI_ERR_BASE + 4,
    ISCSI_ERR_BAD_OPCODE        = ISCSI_ERR_BASE + 5,
    ISCSI_ERR_DATALEN       = ISCSI_ERR_BASE + 6,
    ISCSI_ERR_AHSLEN        = ISCSI_ERR_BASE + 7,
    ISCSI_ERR_PROTO         = ISCSI_ERR_BASE + 8,
    ISCSI_ERR_LUN           = ISCSI_ERR_BASE + 9,
    ISCSI_ERR_BAD_ITT       = ISCSI_ERR_BASE + 10,
    ISCSI_ERR_CONN_FAILED       = ISCSI_ERR_BASE + 11,
    ISCSI_ERR_R2TSN         = ISCSI_ERR_BASE + 12,
    ISCSI_ERR_SESSION_FAILED    = ISCSI_ERR_BASE + 13,
    ISCSI_ERR_HDR_DGST      = ISCSI_ERR_BASE + 14,
    ISCSI_ERR_DATA_DGST     = ISCSI_ERR_BASE + 15,
    ISCSI_ERR_PARAM_NOT_FOUND   = ISCSI_ERR_BASE + 16,
    ISCSI_ERR_NO_SCSI_CMD       = ISCSI_ERR_BASE + 17,
    ISCSI_ERR_INVALID_HOST      = ISCSI_ERR_BASE + 18,
    ISCSI_ERR_XMIT_FAILED       = ISCSI_ERR_BASE + 19,
    ISCSI_ERR_TCP_CONN_CLOSE    = ISCSI_ERR_BASE + 20,
    ISCSI_ERR_SCSI_EH_SESSION_RST   = ISCSI_ERR_BASE + 21,
    ISCSI_ERR_NOP_TIMEDOUT      = ISCSI_ERR_BASE + 22,

    ISCSI_ERR_MAX
};

struct iscsi_conn_stats {
    __u64 conn_err[ISCSI_ERR_MAX - ISCSI_ERR_BASE]; // FROM 'iscsi_conn_error_event'
};

struct iscsi_stats {
    __u32 latency_iscsi_max;        // FROM delta between tracepoint 'scsi_dispatch_cmd_done' and @req->start_time_ns
    __u32 latency_iscsi_avg;        // Same as above
    __u32 latency_iscsi_last;       // Same as above
    __u64 count_iscsi_tmout;        // FROM 'scsi_dispatch_cmd_timeout'
    __u64 count_iscsi_err;          // FROM tracepoint 'scsi_dispatch_cmd_error'
};

struct block_data {
    enum blk_type_e blk_type;       // disk; part
    enum blk_drv_e drv_type;       // iscsi; virtio
    char disk_name[DISK_NAME_LEN];
    struct blk_stats        blk_stats;
    struct iscsi_stats      icsi_stats;
    struct iscsi_conn_stats conn_stats;
    struct blk_sas_stats    sas_stats;
};

#endif
