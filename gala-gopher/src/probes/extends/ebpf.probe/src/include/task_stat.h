/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __TASK_STAT_H__
#define __TASK_STAT_H__

int read_task_stat(unsigned int pid);
long long get_task_minflt(unsigned int read_handle);
long long get_task_majflt(unsigned int read_handle);
long long get_task_utime(unsigned int read_handle);
long long get_task_stime(unsigned int read_handle);
long long get_task_vsize(unsigned int read_handle);
long long get_task_rss(unsigned int read_handle);
void free_task_stat(unsigned int read_handle);

#endif
