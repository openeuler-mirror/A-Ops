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
 * Author: dowzyx
 * Create: 2022-02-10
 * Description: basic task struct
 ******************************************************************************/
#ifndef __GOPHER_TASK_H__
#define __GOPHER_TASK_H__

#define SHARE_MAP_TASK_MAX_ENTRIES 10 * 1024

enum task_status_type {
    TASK_STATUS_ACTIVE = 0,
    TASK_STATUS_INACTIVE,
    TASK_STATUS_INVALID,
    TASK_STATUS_MAX,
};

struct task_key {
    int pid;                // FROM '/proc/[PID]'
};

struct task_io_data {
    int major;
    int minor;
    __u32 fd_count;         // FROM '/usr/bin/ls -l /proc/[PID]/fd | wc -l'

    __u64 task_io_wait_time_us; // FROM tracepoint 'sched_stat_iowait'
    
    __u64 task_wblock_bytes;    // FROM 'blk_account_io_start/blk_mq_start_request/blk_account_io_completion'
    __u64 task_rblock_bytes;    // FROM same as 'task_wblock_bytes'
    __u64 task_io_count;        // FROM same as 'task_wblock_bytes'
    __u64 task_io_time_us;      // FROM same as 'task_wblock_bytes'

    
    __u64 task_rchar_bytes;     // FROM '/proc/[PID]/io'
    __u64 task_wchar_bytes;     // FROM same as 'task_rchar_bytes'
    __u32 task_syscr_count;     // FROM same as 'task_rchar_bytes'
    __u32 task_syscw_count;     // FROM same as 'task_rchar_bytes'
    __u64 task_read_bytes;      // FROM same as 'task_rchar_bytes'
    __u64 task_write_bytes;     // FROM same as 'task_rchar_bytes'
    __u64 task_cancelled_write_bytes;   // FROM same as 'task_rchar_bytes'

    __u32 task_hang_count;      // FROM tracepoint 'sched_process_hang'
};

struct task_id {
    int tgid;                   // task group id
    int ppid;                   // parent process id
    int pgid;                   // process group id
};

struct task_bin {
    char comm[TASK_COMM_LEN];           // FROM '/proc/[PID]/comm'
    char exec_file[TASK_EXE_FILE_LEN];  // executed_file path, eg. xxx.jar
    char exe_file[TASK_EXE_FILE_LEN];   // EXE path, eg. /usr/bin/java
};

struct task_base_data {
    __u32 task_status;
    __u32 fork_count;
};

struct task_data {
    struct task_id id;
    struct task_base_data base;
    struct task_io_data io;
};

#endif
