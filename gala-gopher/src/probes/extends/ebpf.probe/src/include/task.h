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

#define TASK_COMM_LEN           16
#define TASK_EXE_FILE_LEN       128

struct task_key {
    int pid;            // task key
};

struct task_data {
    int tgid;           // task group id
    int ppid;                   // parent process id
    int pgid;                   // process group id
    char comm[TASK_COMM_LEN];
    char exe_file[TASK_EXE_FILE_LEN];   // EXE path, eg. /usr/bin/java
    char exec_file[TASK_EXE_FILE_LEN];  // executed_file path, eg. xxx.jar
    __u32 fork_count;
    __u64 offcpu_time;
    __u64 signal_count;
    __u64 syscall_fails;
    __u32 oom_count;
    __u32 page_cache_count;
    __u32 io_wait_time_max;
};

#endif
