/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __KILLPROBE__H
#define __KILLPROBE__H

#define KILL_INFO_MAX_NUM 100
#define MONITOR_PIDS_MAX_NUM 10
#define TASK_COMM_LEN 16

#define PROBE_CYCLE_SEC (5)

struct val_t {
   __u64 killer_pid;
   int signal;
   int killed_pid;
   char comm[TASK_COMM_LEN];
};

#endif