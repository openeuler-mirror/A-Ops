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
#define CONTAINER_KEY_LEN     (CONTAINER_ID_LEN + 4)
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
    char container_id[CONTAINER_KEY_LEN];
};

struct container_value {
    __u32 proc_id;                          // First process id of container
    __u32 cpucg_inode;                      // cpu group inode of container
    __u32 memcg_inode;                      // memory group inode of container
    __u32 pidcg_inode;                      // pids group inode of container
    __u32 mnt_ns_id;                        // Mount namespace id of container
    __u32 net_ns_id;                        // Net namespace id of container
    __u64 memory_usage_in_bytes;
    __u64 memory_limit_in_bytes;
    __u64 cpuacct_usage;
    __u64 cpuacct_usage_user;
    __u64 cpuacct_usage_sys;
    __u64 pids_current;
    __u64 pids_limit;

    char name[CONTAINER_NAME_LEN];           // Name of container

    char cpucg_dir[PATH_LEN];
    char memcg_dir[PATH_LEN];
    char pidcg_dir[PATH_LEN];
};

struct container_evt_s {
    struct container_key k;
    __u32 crt_or_del;                       // 0: create event; 1: delete event
};

#endif /* __TRACE_CONTAINERD__H */
