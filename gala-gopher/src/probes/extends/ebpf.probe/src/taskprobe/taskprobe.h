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
 * Author: sinever
 * Create: 2021-10-25
 * Description: task_probe include file
 ******************************************************************************/
#ifndef __TASKPROBE__H
#define __TASKPROBE__H

#define TASK_MAP_ENTRY_SIZE     (256 * 10)
#define PROBE_PROC_MAP_ENTRY_SIZE   128
#define MAX_PROCESS_NAME_LEN        128
#define COMMAND_LEN                 256
#define LINE_BUF_LEN                512
#define JAVA_COMMAND_LEN            128
#define JAVA_CLASSPATH_LEN          512
#define TASK_EXIT_MAP_FILE_PATH "/sys/fs/bpf/task_exit_event"

enum ps_type {
    PS_TYPE_PID,
    PS_TYPE_PPID,
    PS_TYPE_PGID,
    PS_TYPE_COMM,
    PS_TYPE_MAX,
};

struct task_metric {
    __u32 ptid;                // parent task id
                               // namespace
    __u64 offcpu_time;
    __u16 fork_count;
    __u64 signal_count;
    __u64 syscall_fails;
    __u32 io_wait_time;
    __u64 utime_jiffies;
    __u64 stime_jiffies;
    __u32 oom_count;
    __u32 minor_pagefault_count;
    __u32 major_pagefault_count;
    __u64 vm_size;
    __u64 pm_size;
    __u32 page_cache_count;
    __u64 shared_dirty_size;
    __u32 shared_clean_size;
    __u64 private_dirty_size;
    __u64 private_clean_size;
    __u64 referenced_size;
    __u32 lazyfree_size;
    __u32 swap_data_size;
    __u32 swap_data_pss_size;
    __u32 fd_count;
    __u32 io_wait_time_max;
    __u64 rchar_bytes;
    __u64 wchar_bytes;
    __u32 syscr_count;
    __u32 syscw_count;
    __u64 read_bytes;
    __u64 write_bytes;
};

/* process needed to be probed */
struct probe_process {
    char name[MAX_PROCESS_NAME_LEN];
};

#endif
