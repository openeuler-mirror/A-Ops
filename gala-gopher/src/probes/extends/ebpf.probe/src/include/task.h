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

struct task_key {
    int pid;                // FROM '/proc/[PID]'
};

struct task_io_data {
    __u32 fd_count;         // FROM '/usr/bin/ls -l /proc/[PID]/fd | wc -l'

    __u64 task_io_wait_time_us; // FROM 'io_schedule_prepare/io_schedule_finish'
    
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
};

struct task_id_data {
    int tgid;                   // task group id
    int ppid;                   // parent process id
    int pgid;                   // process group id
#if !defined( BPF_PROG_KERN ) && !defined( BPF_PROG_USER )   
    char comm[TASK_COMM_LEN];   // FROM '/proc/[PID]/comm'
    char exe_file[TASK_EXE_FILE_LEN];   // EXE path, eg. /usr/bin/java
    char exec_file[TASK_EXE_FILE_LEN];  // executed_file path, eg. xxx.jar
#endif    
};

struct task_base_data {
    __u32 fork_count;
};

struct task_data {
    struct task_id_data id;
    struct task_base_data base;
    struct task_io_data io;
};

#endif
