#ifndef __FILEPROBE__H
#define __FILEPROBE__H

#include "vmlinux.h"

#define SNOOP_FILES_MAX_NUM 100
#define PERMISSION_MAX 10
#define SUSPICIOUS_MAX 100
#define TASK_COMM_LEN 16
#define FILE_NAME_LEN 256
#define OP_TYPE_READ  0x01
#define OP_TYPE_WRITE 0x02

#define PROBE_CYCLE_SEC (5)

struct snoop_evt {
    u64 ts;
    int op_type;
    char file[FILE_NAME_LEN];
    char exe[FILE_NAME_LEN];
};

struct snoop_inode {
    unsigned long inode;
};

struct inode_permissions {
    u32 permission;
    char exe[FILE_NAME_LEN];
};

struct suspicious_op_key {
    unsigned long inode;
    u64 ts;
};

struct suspicious_op_val {
    int op_type;
    char exe[FILE_NAME_LEN];
};

struct snoop_file {
    char file[FILE_NAME_LEN];
    char exe[FILE_NAME_LEN];
    u32  permission;
};

#endif
