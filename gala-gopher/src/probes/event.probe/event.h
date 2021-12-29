#ifndef __EVENTPROBE__H
#define __EVENTPROBE__H

#include <linux/types.h>

#include "base.h"

#define EVENT_LEVEL_INFO  "INFO"
#define EVENT_LEVEL_WARN  "WARN"
#define EVENT_LEVEL_ERROR "ERROR"
#define EVENT_LEVEL_FATAL "FATAL"

struct event_data {
    __u64 timestamp;  // UNIX Epoch time in seconds since 00:00:00 UTC on 1 January 1970.
    char level[16];   // Event level: "INFO"|"WARN"|"ERROR"|"FATAL".
    char body[MAX_DATA_STR_LEN]; 
};

void print_event_output(struct event_data *event);

#endif
