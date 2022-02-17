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

#define PROBE_PROC_MAP_ENTRY_SIZE   128
#define MAX_PROCESS_NAME_LEN        128
//#define TASK_EXIT_MAP_FILE_PATH "/sys/fs/bpf/task_exit_event"

enum ps_type {
    PS_TYPE_PID = 0,
    PS_TYPE_PPID,
    PS_TYPE_PGID,
    PS_TYPE_MAX,
};

/* process needed to be probed */
struct probe_process {
    char name[MAX_PROCESS_NAME_LEN];
};

#endif
