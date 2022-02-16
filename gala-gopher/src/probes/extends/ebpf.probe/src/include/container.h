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
 * Author: Mr.lu
 * Create: 2021-07-26
 * Description: container header file
 ******************************************************************************/
#ifndef __CONTAINER_H__
#define __CONTAINER_H__

#define TEN                 10
#define COER_NUM            16

struct cgroup_metric {
    unsigned long memory_usage_in_bytes;
    unsigned long memory_limit_in_bytes;
    unsigned long memory_stat_cache;
    unsigned long cpuacct_usage;
    unsigned long cpuacct_usage_percpu[COER_NUM];
    unsigned long pids_current;
    unsigned long pids_limit;
};

typedef struct container_info_s {
    unsigned int pid;
    unsigned int netns;
    unsigned int mntns;
    unsigned int cgroup;
    char container[CONTAINER_ID_LEN];
    char pod[POD_NAME_LEN];
    char comm[TASK_COMM_LEN];
} container_info;

typedef struct container_tbl_s {
    unsigned int num;
    container_info *cs;
} container_tbl;

container_tbl* get_all_container(void);
const char* get_container_id_by_pid(container_tbl* cstbl, unsigned int pid);
void free_container_tbl(container_tbl **pcstbl);
int get_container_merged_path(const char *container_id, char *path, unsigned int len);
int exec_container_command(const char *container_id, const char *exec, char *buf, unsigned int len);
void get_container_cgroup_metric(const char *container_id, const char *namespace, struct cgroup_metric *cgroup);

#endif
