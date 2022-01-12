/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __TASKPROBE__H
#define __TASKPROBE__H

#define TASK_MAP_ENTRY_SIZE (256 * 10)

struct task_key {
    __u32 tgid;
    __u32 pid;
};

struct task_kdata {
    __u32 ptid;                // parent task id
    __u32 fork_count;
    __u64 offcpu_time;
    __u64 signal_count;
    __u64 syscall_fails;
    __u32 oom_count;
    __u32 page_cache_count;
    __u32 io_wait_time_max;
};

struct task_data {
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

#endif