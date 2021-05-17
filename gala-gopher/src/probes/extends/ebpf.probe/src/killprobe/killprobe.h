#ifndef __KILLPROBE__H
#define __KILLPROBE__H

#include "vmlinux.h"

#define KILL_INFO_MAX_NUM 100
#define MONITOR_PIDS_MAX_NUM 10
#define TASK_COMM_LEN 16

#define PROBE_CYCLE_SEC (5)

struct val_t {
   u64 killer_pid;
   int signal;
   int killed_pid;
   char comm[TASK_COMM_LEN];
};

#endif
