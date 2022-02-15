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
 * Author: njlzk
 * Create: 2021-10-12
 * Description: provide gala-gopher cmd
 ******************************************************************************/
#ifndef __TRACE_CONTAINERD__H
#define __TRACE_CONTAINERD__H

#define CONTAINER_MAX_ENTRIES   1000
#define SYMADDRS_MAP_KEY      0xacbd

struct go_containerd_t {
    // Arguments of runtime/v1/linux.(*Task).Start.
    int task_Start_t_offset;                // 8

    // Arguments of runtime/v1/linux.(*Task).Delete.
    int task_Delete_t_offset;               // 8
    int task_Delete_resp_offset;            // 24

    // Members of /runtime.Exit
    int runtime_Exit_Pid_offset;            // 0
    int runtime_Exit_Status_offset;         // 4
    int runtime_Exit_Timestamp_offset;      // 8

    // Members of /runtime/v1/linux.Task
    int linux_Task_id_offset;               // 8
    int linux_Task_pid_offset;              // 24
    int linux_Task_namespace_offset;        // 40
    int linux_Task_cg_offset;               // 56
};

struct container_key {
    char container_id[CONTAINER_ID_LEN];
};

struct container_value {
    char namespace[NAMESPACE_LEN];
    __u32 task_pid;
    int containerd_pid;
    __u32 status;
    char comm[16];
    __u64 memory_usage_in_bytes;
    __u64 memory_limit_in_bytes;
    __u64 memory_stat_cache;
    __u64 cpuacct_usage;
    __u64 cpuacct_usage_percpu[16];
    __u64 pids_current;
    __u64 pids_limit;
};

#endif /* __TRACE_CONTAINERD__H */